# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 18:15:56 2021

@author: Andrew

"""

import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

#setting up address twitter mapping
votes = pd.read_csv(r'main_datasets/graph_data/voting_graph_full.csv', index_col=0)
#len(set(df["Voter"].append(df["Voted"]))) 2130 nodes total
votes = votes[votes["Voter"]!=votes["Voted"]] #remove those who voted for self

full_addy = pd.read_csv(r'main_datasets/mirror_supplied/mirror_tv.csv', index_col=0)
full_addy = full_addy.drop_duplicates(subset="username",keep="first") #this is REALLY important since some users have verified more than once, but the votes json file registers only their first signed address
full_addy.address = full_addy.address.apply(lambda x: x.lower())
full_addy.username = full_addy.username.apply(lambda x: x.lower())
handle_eth = dict(zip(full_addy.username,full_addy.address))
votes[["Voter","Voted"]] = votes[["Voter","Voted"]].applymap(lambda x: handle_eth[x.lower()])

print("plotting graph...")
consolidated = pd.read_csv(r'main_datasets/mirror_graph_processed.csv', index_col=["source","target"])
consolidated_melt = consolidated.dropna(subset=["Votes","CF_contribution","ED_purchaseValue","SP_value","AU_value"], how="all").melt(ignore_index=False).dropna() #drop those with just twitter mentions, for art purposes
consolidated_melt.reset_index(inplace=True)
# consolidated_melt = consolidated_melt[consolidated_melt["variable"]=="Votes"] #for eselecting only one to plot

color_key = {"Votes":"#993358","mentions":"#D86044","CF_contribution":"#DC866F","ED_purchaseValue":"#F3A64E","SP_value":"#F3A64E","AU_value":"#F3A64E"}
width_key = {"Votes":1,"mentions":1.5,"CF_contribution":2,"ED_purchaseValue":2,"SP_value":2,"AU_value":2}
alpha_key = {"Votes":1.0,"mentions":0.6,"CF_contribution":0.3,"ED_purchaseValue":0.3,"SP_value":0.3,"AU_value":0.3}

consolidated_melt["color"] = consolidated_melt["variable"].apply(lambda x: color_key[x])
consolidated_melt["width"] = consolidated_melt["variable"].apply(lambda x: width_key[x])
consolidated_melt["alpha"] = consolidated_melt["variable"].apply(lambda x: alpha_key[x])

#setting rules for node_size, assumes betweenness has been calculated already
# cs = pd.read_csv(r'main_datasets\mirror_graph_score_ready.csv')
# top_300_bw = set(cs.sort_values(by="betweenness", ascending=False)["source"][:300])
top_300_bw = {}

#setting rules for color_map 
winners = pd.read_json(r'main_datasets\mirror_supplied\votingdata.json')
winners = list(set(winners[winners.hasPublication==True]["username"]))
winners_eth = [handle_eth[winner.lower()] for winner in winners]

G = nx.from_pandas_edgelist(consolidated_melt, "source","target", 
                            edge_key="variable", 
                            edge_attr=["value","color","width","alpha"],
                            create_using=nx.MultiGraph()) #digraph looks weird af

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

# i=0
# while i<10:
#     plt.figure(figsize=(50, 50))
#     pos = nx.spring_layout(G)
#     nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=10) #size_map)
    
#     for edge in G.edges():
#         attributes = G.get_edge_data(edge[0],edge[1])
#         nx.draw_networkx_edges(G, pos, connectionstyle='arc3, rad = 0.4',
#             edgelist=[edge],
#             width=attributes[next(iter(attributes))]["width"],
#             alpha=attributes[next(iter(attributes))]["alpha"],
#             edge_color=attributes[next(iter(attributes))]["color"])
    
#     # plt.rcParams['axes.facecolor'] = 'xkcd:salmon'
#     plt.axis('off')
#     plt.show() 
#     i+=1

"""community graph analysis (uncomment only when you want to run the algos)"""
print("calculating betweenness...")

"""betweenness"""
# Generate connected components and select the largest:
largest_component = max(nx.connected_components(G), key=len)
# Create a subgraph of G consisting only of this component:
G2 = G.subgraph(largest_component)
betweenness_c= nx.algorithms.centrality.betweenness_centrality_source(G2) #weight="value"

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
consolidated_score.to_csv(r'main_datasets\mirror_graph_score_ready.csv')

##make venn diag on how many people mentioned, voted, and contributed to each other overlap. This could deff be refactored hahaha
from matplotlib_venn import venn3
import matplotlib.pyplot as plt
consolidated_score = pd.read_csv(r'main_datasets\mirror_graph_score_ready.csv')

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
