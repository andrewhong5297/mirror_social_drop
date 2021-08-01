# -*- coding: utf-8 -*-
"""
Created on Sat Jul 31 18:15:56 2021

@author: Andrew

"""

import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

#setting up address twitter mapping
votes = pd.read_csv(r'main_datasets/graph_data/voting_graph_full.csv', index_col=0)
votes = votes[votes["Votes"]!=0] #seems like some error in the json file
#len(set(df["Voter"].append(df["Voted"]))) 2130 nodes total
votes = votes[votes["Voter"]!=votes["Voted"]] #remove those who voted for self

full_addy = pd.read_csv(r'main_datasets/mirror_supplied/mirror_tv.csv', index_col=0)
full_addy = full_addy.drop_duplicates(subset="username",keep="first") #this is REALLY important since some users have verified more than once, but the votes json file registers only their first signed address
full_addy.address = full_addy.address.apply(lambda x: x.lower())
full_addy.username = full_addy.username.apply(lambda x: x.lower())
handle_eth = dict(zip(full_addy.username,full_addy.address))
votes[["Voter","Voted"]] = votes[["Voter","Voted"]].applymap(lambda x: handle_eth[x.lower()])

"""weighting edges into single graph"""
consolidated = pd.read_csv(r'main_datasets/mirror_graph_processed.csv', index_col=["source","target"])
consolidated.fillna(0, inplace=True)

#weight by total mentions given (is there any way to do this without a pivot/join?)
mentions_pivot = consolidated.reset_index().pivot_table(index="source",values="mentions",aggfunc="sum")
mentions_pivot.columns=["total_mentions"]
consolidated = pd.merge(consolidated.reset_index(),mentions_pivot.reset_index(),how="left",on="source").set_index(["source","target"])

#weight by total contributions (need a total calc)
contributions_pivot = consolidated.reset_index().pivot_table(index="source",
                                                        values=["CF_contribution","ED_purchaseValue","SP_value","AU_value"]
                                                        ,aggfunc="sum")
contributions_pivot.columns=["AU_total","CF_total","ED_total","SP_total"]
consolidated = pd.merge(consolidated.reset_index(),contributions_pivot.reset_index(),how="left",on="source").set_index(["source","target"])

#weight by total votes given (total calc)
votes_pivot = consolidated.reset_index().pivot_table(index="source",values="Votes",aggfunc="sum")
votes_pivot.columns=["total_votes"]
consolidated = pd.merge(consolidated.reset_index(),votes_pivot.reset_index(),how="left",on="source").set_index(["source","target"])

###normalize all
consolidated["mentions2"] = consolidated["mentions"].div(consolidated["total_mentions"])
consolidated["Votes2"] = consolidated["Votes"].div(consolidated["total_votes"])
consolidated["CF_contribution2"] = consolidated["CF_contribution"].div(consolidated["CF_total"])
consolidated["ED_purchaseValue2"] = consolidated["ED_purchaseValue"].div(consolidated["ED_total"])
consolidated["SP_value2"] = consolidated["SP_value"].div(consolidated["SP_total"])
consolidated["AU_value2"] = consolidated["AU_value"].div(consolidated["AU_total"])

consolidated.replace(np.inf, 0, inplace=True)
consolidated.fillna(0,inplace=True)

#weighted edge multiples should add up to a maximum of 10
#this might also need to be weighted by total... so normalized first? 
consolidated["weighted_edge"]=30*consolidated["mentions2"] \
                                + 30*consolidated["Votes2"] \
                                + 10*consolidated["CF_contribution2"] \
                                + 10*consolidated["ED_purchaseValue2"] \
                                + 10*consolidated["SP_value2"] \
                                + 10*consolidated["AU_value2"]

consolidated = consolidated[~consolidated.eq(0).all(1)] 
consolidated = consolidated.drop(columns=["CF_total","ED_total","SP_total","AU_total","total_votes","total_mentions"])
consolidated = consolidated.drop(columns=["CF_contribution2","ED_purchaseValue2","SP_value2","AU_value2","Votes2","mentions2"])

"""plots"""
print("plotting graph...")
#setting rules for node_size, assumes betweenness has been calculated already
# cs = pd.read_csv(r'main_datasets\mirror_graph_score_ready_weighted.csv')
# top_300_bw = set(cs.sort_values(by="betweenness", ascending=False)["source"][:300])
top_300_bw = {}

#setting rules for color_map 
winners = pd.read_json(r'main_datasets\mirror_supplied\votingdata.json')
winners = list(set(winners[winners.hasPublication==True]["username"]))
winners_eth = [handle_eth[winner.lower()] for winner in winners]

G = nx.from_pandas_edgelist(consolidated.reset_index(), edge_attr=["weighted_edge"],
                                   create_using=nx.DiGraph())

# color_map = []
# for node in G:
#     if node in top_300_bw:
#         color_map.append("red")
#     elif node in winners_eth:
#         color_map.append("#FDED66")
#     else:
#         color_map.append("#1B4DCC")

# # size_map = []
# # for node in G:
# #     # print(node)
# #     if node in top_300_bw:
# #         size_map.append(30)
# #     else:
# #         size_map.append(10)
        
# # nx.write_gexf(G , r'main_datasets/social_graph.gexf')

# plt.figure(figsize=(50, 50))
# pos = nx.spring_layout(G)
# nx.draw_networkx(G, pos, connectionstyle='arc3, rad = 0.1', node_color=color_map, node_size=10, with_labels=False) #size_map) 
# #maybe find a way to add the curves to lines https://stackoverflow.com/questions/15053686/networkx-overlapping-edges-when-visualizing-multigraph

# plt.axis('off')
# plt.show() 

"""community graph analysis (uncomment only when you want to run the algos)"""
print("calculating betweenness...")

"""betweenness"""
# # Generate connected components and select the largest: (doesn't work for digraph)
# largest_component = max(nx.connected_components(G), key=len)
# # Create a subgraph of G consisting only of this component:
# G2 = G.subgraph(largest_component)
betweenness_c= nx.algorithms.centrality.betweenness_centrality_source(G, weight="weighted_edge")

"""putting into df"""
eth_handle = dict(zip(full_addy.address,full_addy.username))
def try_handle(x):
    try:
        return eth_handle[x]
    except:
        pass
    
def try_betweenness(x, betweenness):
    try:
        return betweenness[x]
    except:
        return betweenness[min(betweenness, key=betweenness.get)] #minimum value

consolidated_score = consolidated.reset_index().pivot_table(index=["source"],values=["Votes","CF_contribution","ED_purchaseValue","SP_value","AU_value","mentions"]
                                                            ,aggfunc="sum").reset_index()
consolidated_score["twitter"] = consolidated_score["source"].apply(lambda x: try_handle(x))

consolidated_score["betweenness"] = consolidated_score["source"].apply(lambda x: try_betweenness(x, betweenness_c))
consolidated_score["betweenness"] = consolidated_score["betweenness"] - min(consolidated_score["betweenness"]) #must be base 0

print("saved!")
consolidated_score.to_csv(r'main_datasets\mirror_graph_score_ready_weighted.csv')

"""venn diagram plot"""
from matplotlib_venn import venn3
import matplotlib.pyplot as plt
consolidated_score = pd.read_csv(r'main_datasets\mirror_graph_score_ready_weighted.csv')

total_voters = len(set(consolidated_score[consolidated_score["Votes"]!=0]["source"]))
total_twitters = len(set(consolidated_score[consolidated_score["mentions"]!=0]["source"]))
total_funders = len(set(consolidated_score[(consolidated_score["CF_contribution"]!=0) | (consolidated_score["ED_purchaseValue"]!=0) 
                                  | (consolidated_score["SP_value"]!=0) | (consolidated_score["AU_value"]!=0)]["source"]))

total_voters_twitters = len(set(consolidated_score[(consolidated_score["Votes"]!=0) & (consolidated_score["mentions"]!=0)]["source"]))

total_voters_funders = len(set(consolidated_score[(consolidated_score["Votes"]!=0) & ((consolidated_score["CF_contribution"]!=0) | (consolidated_score["ED_purchaseValue"]!=0 )
                                  | (consolidated_score["SP_value"]!=0) | (consolidated_score)["AU_value"]!=0)]["source"]))

total_funders_twitters = len(set(consolidated_score[(consolidated_score["mentions"]!=0) & ((consolidated_score["CF_contribution"]!=0) | (consolidated_score["ED_purchaseValue"]!=0)
                                  | (consolidated_score["SP_value"]!=0) | (consolidated_score["AU_value"]!=0))]["source"]))

total_funders_twitters_voters =  len(set(consolidated_score[(consolidated_score["Votes"]!=0) & (consolidated_score["mentions"]!=0) & ((consolidated_score["CF_contribution"]!=0) | (consolidated_score["ED_purchaseValue"]!=0) 
                                  | (consolidated_score["SP_value"]!=0) | (consolidated_score["AU_value"]!=0))]["source"]))

fig, ax = plt.subplots(figsize=(10,10))
venn3(subsets = (total_voters, total_twitters, total_voters_twitters, total_funders, total_voters_funders, total_funders_twitters, total_funders_twitters_voters), 
      set_labels = ('$WRITE Race', 'Twitter', 'Contributors (Ethereum Txs)'), set_colors=('r', 'g', 'b'), alpha = 0.5, ax =ax);
