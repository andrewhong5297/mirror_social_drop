# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 15:58:00 2021

@author: Andrew

"""
import pandas as pd
import numpy as np
from sklearn import preprocessing

"""

start recon for calcuating rewards

"""
consolidated_score = pd.read_csv(r'main_datasets\mirror_graph_score_ready.csv', index_col=0)

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

consolidated_score["created"] = consolidated_score["source"].apply(lambda x: count_created(x))

"""calculate unique contrib count"""
#crowdfunding
cf_graph = pd.read_csv(r'main_datasets/graph_data/crowdfunds_graph.csv')

#editions
ed_graph = pd.read_csv(r'main_datasets/graph_data/editions_graph.csv')

#splits
sp_graph = pd.read_csv(r'main_datasets/graph_data/splits_graph.csv', index_col=0)

#auctions
au_graph = pd.read_csv(r'main_datasets/graph_data/auctions_graph.csv')

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

consolidated_score["unique_contributed"] = consolidated_score["source"].apply(lambda x: try_unique(x))

min_max_scaler = preprocessing.MinMaxScaler()

consolidated_score["unique_contributed"] = min_max_scaler.fit_transform(consolidated_score[["unique_contributed"]]) #normalized

"""add in existing votes and other voters"""
votes_df = pd.read_json(r'main_datasets\mirror_supplied\votingdata.json')
votes_before_dict = dict(zip(votes_df["account"].apply(lambda x: x.lower()),votes_df.originalVotingPower))

def assign_old_votes(x):
    try:
        return votes_before_dict[x]
    except:
        return 0
    
consolidated_score["votes_before"] = consolidated_score["source"].apply(lambda x: assign_old_votes(x))

#this runs pretty slow rn lol
votes_df["account"] = votes_df["account"].apply(lambda x: x.lower())
votes_df = votes_df[~votes_df["account"].isin(consolidated_score["source"])]
for index, row in votes_df.iterrows():
    new_row = {"source":row["account"],"votes_before":row["originalVotingPower"],"twitter":row["username"]}
    consolidated_score = consolidated_score.append(new_row, ignore_index=True)

# """add of bidder boolean from dune""" 
# bidders = pd.read_csv(r'main_datasets/dune_data/mirror_au_all_bidders.csv')
# bidders = list(bidders.applymap(lambda x: x.replace('\\','0'))["sender"])

# def did_bid(x):
#     if x in bidders:
#         return 1
#     else:
#         return 0

# consolidated_score["did_bid"] = consolidated_score["source"].apply(lambda x: did_bid(x))

"""rewards simulations"""
consolidated_score.fillna(0,inplace=True)

contract_addresses = ['0xff2f509668048d4fde4f40fedab3334ce104a39b','0x612e8126b11f7d2596be800278ecf2515c85aa5b','0x60e3fb18828a348e5bbb66fa06371933370c0209']

consolidated_score = consolidated_score[~consolidated_score["source"].isin(contract_addresses)]

# did_contribute = set(consolidated_score[(consolidated_score["CF_contribution"]!=0) | (consolidated_score["ED_purchaseValue"]!=0) 
#                      | (consolidated_score["SP_value"]!=0) | (consolidated_score["AU_value"]!=0) | (consolidated_score["did_bid"]!=0)]["source"])
consolidated_score["total_contributions"] = consolidated_score["CF_contribution"]+consolidated_score["ED_purchaseValue"]+consolidated_score["AU_value"]+consolidated_score["SP_value"]

creator_reward = 1
contributor_reward = 2

# consolidated_score["did_contribute"] = consolidated_score["source"].apply(lambda x: contributor_reward if x in did_contribute else 0)
consolidated_score["did_create"] = consolidated_score["created"].apply(lambda x: creator_reward if x > 0 else 0)

consolidated_score["actual_airdrop"] = (consolidated_score["betweenness"]+1)*\
                                            (\
                                             3*consolidated_score["votes_before"].div(1000)\
                                            + consolidated_score["did_create"]\
                                            + (consolidated_score["did_contribute"]*consolidated_score["total_contributions"]*consolidated_score["unique_contributed"]).div(10)\
                                            )

"""Finally, the total airdrop including currently held $WRITE tokens"""
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.offline import plot

consolidated_score["betweenness_level"] = ["high" if betweenness > 0.05 else "low" for betweenness in consolidated_score["betweenness"]]
address_betweenness = dict(zip(consolidated_score.source, consolidated_score.betweenness_level))

def check_distribution(df):
    # for_boxplot = df[["source","actual_airdrop","twitter"]]
    # for_boxplot.set_index("source",inplace=True)
    # for_boxplot.reset_index(inplace=True)
    # for_boxplot["betweenness_level"] = for_boxplot["source"].apply(lambda x: address_betweenness[x])
    
    # for_boxplot["actual_airdrop_log"] = for_boxplot["actual_airdrop"].apply(lambda x: np.log(x))
    # for_boxplot["actual_airdrop_log"] = for_boxplot["actual_airdrop_log"].replace(-np.inf,0)
    
    # # fig = px.box(for_boxplot, x="betweenness_level", y="actual_airdrop_log", hover_data=["twitter"])
    # # plot(fig,"main_datasets/rewards.html")

    # fig, ax = plt.subplots(figsize=(10,10))
    # sns.boxplot(x="betweenness_level", y="actual_airdrop_log", 
    #                 # hue="betweenness_level", split=True,
    #                 data=for_boxplot, ax=ax)
    # sns.despine(offset=10, trim=True)
    # ax.set(title="Airdrop Allocation (Logarithmic)")
    print("Total tokens distributed: {}".format(sum(consolidated_score["actual_airdrop"])))

check_distribution(consolidated_score)

consolidated_score.to_csv(r'main_datasets\mirror_baseAirdrop.csv')
#maybe this should go into a datapane
consolidated_score.drop(columns="twitter").to_csv(r'main_datasets\mirror_finalAirdrop_cleaned.csv')

