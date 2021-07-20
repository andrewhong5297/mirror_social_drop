# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 15:58:00 2021

@author: Andrew

"""
import pandas as pd

"""

start recon for calcuating rewards

"""
#this has V_contributed, hasVoted, centrality, and betweenness captured. so you'll need to add created # and unique supported values
consolidated_df = pd.read_csv(r'main_datasets\mirror_graph_score_ready.csv', index_col=0)

"""calculate created count"""
#entries created
ent = pd.read_csv(r'main_datasets\mirror_supplied\Entries_created.csv')
ent.address = ent.address.apply(lambda x: x.lower())
created_ent = dict(zip(ent.address,ent.num_entries))

cf = pd.read_csv(r'main_datasets\mirror_supplied\Crowdfunds.csv')
cf["creator"] = cf["creator"].apply(lambda x: x.lower())
created_cf = cf.pivot_table(index="creator",values="contract_address",aggfunc=lambda x: len(x.unique()))
created_cf = dict(zip(created_cf.index,created_cf.contract_address))

ed = pd.read_csv(r'main_datasets\mirror_supplied\Editions.csv')
ed["creator"] = ed["creator"].apply(lambda x: x.lower())
created_ed = ed.pivot_table(index="creator",values="edition_name",aggfunc=lambda x: len(x.unique()))
created_ed = dict(zip(created_ed.index,created_ed.edition_name))

au = pd.read_csv(r'main_datasets\mirror_supplied\ReserveAuctions.csv')
au["creator"] = au["creator"].apply(lambda x: x.lower())
created_au = au.pivot_table(index="creator",values="token_id",aggfunc=lambda x: len(x.unique()))
created_au = dict(zip(created_au.index,created_au.token_id))

sp = pd.read_csv(r'main_datasets\mirror_supplied\Splits.csv')
sp["creator"] = sp["creator"].apply(lambda x: x.lower())
created_sp = sp.pivot_table(index="creator",values="contract_address",aggfunc=lambda x: len(x.unique()))
created_sp = dict(zip(created_sp.index,created_sp.contract_address))

def count_created(x):
    total = 0
    if x in created_cf:
        total += created_cf[x]
    if x in created_ed:
        total += created_ed[x]
    if x in created_au:
        total += created_au[x]
    if x in created_sp:
        total += created_sp[x]
    if x in created_ent:
        total += created_ent[x]
    return total 

consolidated_df["created"] = consolidated_df["source"].apply(lambda x: count_created(x))

"""calculate unique contrib count"""
#crowdfunding
cf_graph = pd.read_csv(r'main_datasets/crowdfunds_graph.csv')

#editions
ed_graph = pd.read_csv(r'main_datasets/editions_graph.csv')

#splits
sp_graph = pd.read_csv(r'main_datasets/splits_graph.csv', index_col=0)

#auctions
au_graph = pd.read_csv(r'main_datasets/auctions_graph.csv')

#concat all
all_contributions = pd.concat([cf_graph[["source","target"]],ed_graph[["source","target"]],
                               sp_graph[["source","target"]],au_graph[["source","target"]]])

unique_contributions_df = all_contributions.pivot_table(index="source",values="target",aggfunc=lambda x: len(x.unique()))
unique_contributions = dict(zip(unique_contributions_df.index,unique_contributions_df["target"]))

def try_unique(x):
    try:
        return unique_contributions[x]
    except:
        return 0

consolidated_df["unique_contributed"] = consolidated_df["source"].apply(lambda x: try_unique(x))

from sklearn import preprocessing
min_max_scaler = preprocessing.MinMaxScaler()

consolidated_df["unique_contributed"] = min_max_scaler.fit_transform(consolidated_df[["unique_contributed"]]) #normalized

"""simulate rewards"""
import numpy as np
def calculate_rewards(df,a,b,c,d):
    #this function is explained in the airdrop proposal
    # changed uniqueness to betweenness, it helps cap it a little but doesn't change distribution.
    # rewardColumn = (1/a*df["closeness"])*((df["betweenness"]*b*df["created"])+\
    #                                     (df["uniqueness"]*(df["CF_contribution"]+df["ED_purchaseValue"]))\
    #                                         +c*df["hasVoted"]*1)\
    #                 /d 
    rewardColumn = df["created"]+(df["CF_contribution"]+df["ED_purchaseValue"]+df["SP_value"]+df["AU_value"])
    return rewardColumn

a_range = np.arange(0.1,1,0.01) #spread of rewards gets thinner as this increases (constant in front of inverse centrality)
#can we store all results and then boxplot? 

consolidated_df["tokenRewards"]= calculate_rewards(consolidated_df,a=0.5,b=10,c=0.5,d=1)
print("Total tokens distributed: {}".format(sum(consolidated_df["tokenRewards"])))

"""Finally, the total airdrop including currently held $WRITE tokens"""
import matplotlib.pyplot as plt
import seaborn as sns
consolidated_df["centrality_level"] = ["high" if closeness > 0.33 else "low" for closeness in consolidated_df["closeness"]]
address_centrality = dict(zip(consolidated_df.source, consolidated_df.centrality_level))

votes_before = pd.read_json(r'main_datasets\mirror_supplied\votingdata.json')
# votes_before.to_csv(r'main_datasets\votingdata_cleaning.csv')
votes_before_dict = dict(zip(votes_before["account"].apply(lambda x: x.lower()),votes_before.originalVotingPower))

def assign_old_votes(x):
    try:
        return votes_before_dict[x]
    except:
        return 0
    
consolidated_df["votes_before"] = consolidated_df["source"].apply(lambda x: assign_old_votes(x))
consolidated_df["actualAirdrop"] = consolidated_df["tokenRewards"] + consolidated_df["votes_before"].div(1000) #add on current votes
consolidated_df["votes_after"] = consolidated_df["actualAirdrop"]*1000

for_boxplot = consolidated_df[["source","votes_before","votes_after"]]
for_boxplot.set_index("source",inplace=True)
for_boxplot = for_boxplot.melt(ignore_index=False)
for_boxplot.columns=["state","votes_allocated"]
for_boxplot.reset_index(inplace=True)
for_boxplot["centrality_level"] = for_boxplot["source"].apply(lambda x: address_centrality[x])

for_boxplot["votes_allocated_log"] = for_boxplot["votes_allocated"].apply(lambda x: np.log(x))
for_boxplot["votes_allocated_log"] = for_boxplot["votes_allocated_log"].replace(-np.inf,0)

# sns.histplot(data=for_boxplot, x="votes_allocated_log", hue="state", kde=True)

#could add hue here for community, i.e. writer and non writer? or by centrality > and < 0.3? 
fig, ax = plt.subplots(figsize=(10,10))
sns.violinplot(x="state", y="votes_allocated_log", 
               hue="centrality_level", split=True,
               data=for_boxplot, ax=ax)
sns.despine(offset=10, trim=True)
ax.set(title="Votes Allocated Before and After Airdrop (Logarithmic)")

# for_kde = consolidated_df[["votes_before","votes_after"]]
# for_kde = for_kde.apply(lambda x: np.log(x))
# for_kde = for_kde.replace(-np.inf,0)

# fig, ax = plt.subplots(figsize=(8,8))
# sns.kdeplot(
#     x=for_kde["votes_before"], y=for_kde["votes_after"],
#     cmap="rocket_r", fill=True,
#     clip=(-5, 5), cut=10,
#     thresh=0, levels=15,
#     ax=ax,
#     )
# ax.set_axis_off()
# ax.set(xlim=(0.1, 0.4), ylim=(-0.1, 0.05))

final_airdrop = consolidated_df[["source","twitter","actualAirdrop"]]

all_votes = votes_before[["account","username","originalVotingPower"]]
all_votes.columns = ["source", "twitter", "actualAirdrop"]
all_votes = all_votes[~all_votes["source"].isin(final_airdrop["source"])]
all_votes["source"] = all_votes["source"].apply(lambda x: x.lower())
all_votes["actualAirdrop"] = all_votes["actualAirdrop"].div(1000)

pd.concat([final_airdrop,all_votes]).drop_duplicates(subset="source", keep="first").to_csv(r'main_datasets\mirror_finalAirdrop.csv')

