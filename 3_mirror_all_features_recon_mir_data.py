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

consolidated_score = pd.read_csv(r'main_datasets\mirror_graph_score_ready_weighted.csv', index_col=0)

"""calculate created count (hopefully this can be replaced with Dune too after factory decoding)"""
all_creations = pd.read_csv(r'main_datasets\dune_data\mirror_all_creations.csv')
all_creations["creator"] = all_creations["creator"].apply(lambda x: x.replace("\\","0"))

#entries created
ent = pd.read_csv(r'main_datasets\mirror_supplied\Entries_created.csv')
ent.address = ent.address.apply(lambda x: x.lower())
created_ent = dict(zip(ent.address,ent.num_entries))

created_cf = all_creations[all_creations["product_type"]=="crowdfund"].pivot_table(index="creator",values="product_type",aggfunc="count") #extra 2 (seems right)
created_cf = dict(zip(created_cf.index,created_cf.product_type))

created_ed = all_creations[all_creations["product_type"]=="editions"].pivot_table(index="creator",values="product_type",aggfunc="count") #extra 2 (seems right)
created_ed = dict(zip(created_ed.index,created_ed.product_type))

created_au = all_creations[all_creations["product_type"]=="reserve_auctions"].pivot_table(index="creator",values="product_type",aggfunc="count") #extra 2 (seems right)
created_au = dict(zip(created_au.index,created_au.product_type))

created_sp = all_creations[all_creations["product_type"]=="splits"].pivot_table(index="creator",values="product_type",aggfunc="count") #extra 3 (seems right)
created_sp = dict(zip(created_sp.index,created_sp.product_type))

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
sp_graph = pd.read_csv(r'main_datasets/graph_data/splits_graph.csv')

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
votes_df = pd.read_json(r'main_datasets\mirror_supplied\votes.json')
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

"""add of bidder boolean from dune""" 
bidders = pd.read_csv(r'main_datasets/dune_data/mirror_au_all_bidders.csv')
bidders = list(bidders.applymap(lambda x: x.replace('\\','0'))["sender"])

def did_bid(x):
    if x in bidders:
        return 1
    else:
        return 0

consolidated_score["did_bid"] = consolidated_score["source"].apply(lambda x: did_bid(x))

"""rewards simulations"""
print("calculating score...")

consolidated_score.fillna(0,inplace=True)

#these filters are still in here cause of splits being from Graeme rather than dune
contract_addresses = ['0xff2f509668048d4fde4f40fedab3334ce104a39b','0x612e8126b11f7d2596be800278ecf2515c85aa5b','0x60e3fb18828a348e5bbb66fa06371933370c0209']

consolidated_score = consolidated_score[~consolidated_score["source"].isin(contract_addresses)]

did_contribute = set(consolidated_score[(consolidated_score["CF_contribution"]!=0) | (consolidated_score["ED_purchaseValue"]!=0) 
                      | (consolidated_score["SP_value"]!=0) | (consolidated_score["AU_value"]!=0) | (consolidated_score["did_bid"]!=0)]["source"])
consolidated_score["total_contributions"] = consolidated_score["CF_contribution"]+consolidated_score["ED_purchaseValue"]+consolidated_score["AU_value"]+consolidated_score["SP_value"]

creator_reward = 0.5
contributor_reward = 0.1

consolidated_score["did_contribute"] = consolidated_score["source"].apply(lambda x: contributor_reward if x in did_contribute else 0)
consolidated_score["did_create"] = consolidated_score["created"].apply(lambda x: creator_reward if x > 0 else 0)

consolidated_score["actual_airdrop"] = (consolidated_score["betweenness"]+1)*\
                                            (\
                                             consolidated_score["percentage_votes_used"]*consolidated_score["votes_before"].div(1000)\
                                            + consolidated_score["did_create"]\
                                            + (consolidated_score["did_contribute"]\
                                               *consolidated_score["total_contributions"]*consolidated_score["unique_contributed"]) \
                                            )

print("Total tokens distributed: {}".format(sum(consolidated_score["actual_airdrop"])))
consolidated_score.to_csv(r'main_datasets\mirror_baseAirdrop_w.csv')
consolidated_score.drop(columns="twitter").to_csv(r'main_datasets\mirror_finalAirdrop_cleaned_w.csv')

###outdated spread analysis
# import matplotlib.pyplot as plt
# import seaborn as sns
# import plotly.express as px
# from plotly.offline import plot

# consolidated_score["betweenness_level"] = ["high" if betweenness > 0.05 else "low" for betweenness in consolidated_score["betweenness"]]
# address_betweenness = dict(zip(consolidated_score.source, consolidated_score.betweenness_level))

# def check_distribution(df):
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

# check_distribution(consolidated_score)
