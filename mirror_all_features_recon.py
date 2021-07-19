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
cf = pd.read_csv(r'main_datasets\dune_data\mirror_cf_contonly.csv', index_col=0)
created_cf = cf.pivot_table(index="creator",values="contract_address",aggfunc=lambda x: len(x.unique()))
created_cf = dict(zip(created_cf.index,created_cf.contract_address))

ed = pd.read_csv(r'main_datasets\dune_data\mirror_ed_freq.csv')
created_ed = dict(zip(ed.creator,ed.editionsCreated))

def count_created(x):
    total = 0
    if x in created_cf:
        total += created_cf[x]
    if x in created_ed:
        total += created_ed[x]
    return total 

consolidated_df["created"] = consolidated_df["source"].apply(lambda x: count_created(x))

"""calculate created count"""
ed = pd.read_csv(r'main_datasets\dune_data\mirror_ed_graph.csv', index_col=0)
ed.columns=["contributor","valuebought","creator"]

#concat all
all_contributions = pd.concat([cf[["contributor","creator"]],ed[["contributor","creator"]]])

unique_contributions_df = all_contributions.pivot_table(index="contributor",values="creator",aggfunc=lambda x: len(x.unique()))
unique_contributions = dict(zip(unique_contributions_df.index,unique_contributions_df["creator"]))

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
    rewardColumn = (1/a*df["closeness"])*((df["betweenness"]*b*df["created"])+\
                                        (df["unique_contributed"]*(df["CF_contribution"]+df["ED_purchaseValue"]))\
                                            +c*1)\
                    /d 
    return rewardColumn

a_range = np.arange(0.1,1,0.01) #spread of rewards gets thinner as this increases (constant in front of inverse centrality)
#can we store all results and then boxplot? 

consolidated_df["tokenRewards"]= calculate_rewards(consolidated_df,a=0.5,b=10,c=0.5,d=1)
print("Total tokens distributed: {}".format(sum(consolidated_df["tokenRewards"])))

"""Finally, the total airdrop including currently held $WRITE tokens"""
import matplotlib.pyplot as plt
import seaborn as sns
consolidated_df["influence_level"] = ["high" if closeness > 0.33 else "low" for closeness in consolidated_df["closeness"]]
address_influence = dict(zip(consolidated_df.source, consolidated_df.influence_level))

votes_before = pd.read_json(r'main_datasets\votingdata.json')
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
for_boxplot["influence_level"] = for_boxplot["source"].apply(lambda x: address_influence[x])

for_boxplot["votes_allocated_log"] = for_boxplot["votes_allocated"].apply(lambda x: np.log(x))
for_boxplot["votes_allocated_log"] = for_boxplot["votes_allocated_log"].replace(-np.inf,0)

# sns.histplot(data=for_boxplot, x="votes_allocated_log", hue="state", kde=True)

#could add hue here for community, i.e. writer and non writer? or by centrality > and < 0.3? 
fig, ax = plt.subplots(figsize=(10,10))
sns.violinplot(x="state", y="votes_allocated_log", 
               hue="influence_level", split=True,
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

consolidated_df[["source","twitter","actualAirdrop"]].to_csv(r'main_datasets\mirror_finalAirdrop.csv')

