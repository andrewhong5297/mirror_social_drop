# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 18:15:56 2021

@author: Andrew

need to refactor this into 4 different scripts lol

"""

import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn import preprocessing

"""
network graph, multi directional

https://towardsdatascience.com/customizing-networkx-graphs-f80b4e69bedf

"""


print("starting preprocessing...")
# df = pd.read_json(r'main_datasets\votingdata.json')

# vote_graph = pd.DataFrame(columns=["Voter","Votes","Voted"])

# for index, row in tqdm(df.iterrows()):
#     for backer in row["backers"]:
#         new_row = {"Voter":backer["username"],"Votes":backer["amount"],"Voted":row["username"]}
#         vote_graph = vote_graph.append(new_row, ignore_index=True)
        
# len(set(vote_graph["Voter"])) #only 2041 out of 7000 handle have voted?

# vote_graph.to_csv(r'main_datasets\voting_graph_full.csv')

votes = pd.read_csv(r'main_datasets\voting_graph_full.csv', index_col=0)
#len(set(df["Voter"].append(df["Voted"]))) 2130 nodes total
votes = votes[votes["Voter"]!=votes["Voted"]] #remove those who voted for self

#this should be the only place ethereum to twitter address is used
full_addy = pd.read_csv(r'main_datasets/mirror_supplied/mirror_tv.csv', index_col=0)
# verified_num = full_addy.pivot_table(index="username", values="address", aggfunc="count")
full_addy = full_addy.drop_duplicates(subset="username",keep="first") #this is REALLY important since some users have verified more than once, but the votes json file registers only their first signed address
full_addy.address = full_addy.address.apply(lambda x: x.lower())
full_addy.username = full_addy.username.apply(lambda x: x.lower())
handle_eth = dict(zip(full_addy.username,full_addy.address))
votes[["Voter","Voted"]] = votes[["Voter","Voted"]].applymap(lambda x: handle_eth[x.lower()])

"""

add in ethereum transaction data to graph network and save file as consolidated

- any removal of QA and overlapping addresses will need to be done in this block

"""

# consolidated = votes.pivot_table(index=["Voter","Voted"], values="Votes", aggfunc="sum")
# consolidated.index.names=["source","target"]

# #crowdfunds
# cf = pd.read_csv(r'main_datasets\dune_data\mirror_cf_all_graph.csv')

# #3 creators are missing from dune logs for some reason
# missing_creator = {'\\x41ed7d49292b8fbf9b9311c1cb4d6eb877646c58':'0x48A63097E1Ac123b1f5A8bbfFafA4afa8192FaB0', 
#                    '\\xa338f6960d1e8bcde50a8057173229dcaa4428c9':'0xA0Cf798816D4b9b9866b5330EEa46a18382f251e',
#                    '\\x94515e4f6fabad73c8bcdd8cd42f0b5c037e2c49': '0xc3268ddb8e38302763ffdc9191fcebd4c948fe1b'}

# def fill_missing_creators(x):
#     try:
#         return missing_creator[x]
#     except:
#         return x

# cf["creator"] = cf["contract_address"].apply(lambda x: fill_missing_creators(x)) 
# cf[["contributor","contract_address","creator"]]=cf[["contributor","contract_address","creator"]].applymap(lambda x: x.replace("\\","0"))
# cf_graph = cf.pivot_table(index=["contributor","creator"],values="contribution",aggfunc="sum")
# cf_graph.index.names=["source","target"]
# cf_graph.columns=["CF_contribution"]
# cf_graph.to_csv(r'main_datasets/crowdfunds_graph.csv')

# #editions
# ed = pd.read_csv(r'main_datasets\dune_data\mirror_ed_all_graph.csv') #could join with timestamp too in future, would need more accurate timestamp from mirror supplied data
# ed[["buyer","contract_address","fundingRecipient"]]=ed[["buyer","contract_address","fundingRecipient"]].applymap(lambda x: x.replace("\\","0"))
# ed_creator = pd.read_csv(r'main_datasets\mirror_supplied\Editions.csv')
# ed_creator[["contract_address","creator","fundingRecipient"]] = ed_creator[["contract_address","creator","fundingRecipient"]].applymap(lambda x: x.lower())
# ed_creator = ed_creator.drop_duplicates(subset=["contract_address","creator","fundingRecipient","edition_name"])
# ed_merged = pd.merge(ed,ed_creator, how="left", on=["contract_address","org_quantity","fundingRecipient","org_price"])

# ed_graph = ed_merged.pivot_table(index=["buyer","creator"],values="valuebought",aggfunc="sum")
# ed_graph.index.names=["source","target"]
# ed_graph.columns=["ED_purchaseValue"]
# ed_graph.to_csv(r'main_datasets/editions_graph.csv')

# #splits
# sp = pd.read_json('main_datasets/mirror_supplied/SplitsContributions.json')
# sp.rename(columns={'name':'split_name','address':'contract_address'}, inplace=True)
# sp_creator = pd.read_csv(r'main_datasets\mirror_supplied\Splits.csv')
# sp_creator["creator"] = sp_creator["creator"].apply(lambda x: x.lower())
# sp_merged = pd.merge(sp,sp_creator, how="left",on="contract_address")

# graph_cols = ["source","SP_value","target"]
# sp_graph = pd.DataFrame(columns=graph_cols)

# for index, row in sp_merged.iterrows():
#     tips = row["contributions"]
#     for tip in tips:
#         new_row = {"source": tip["from"], "SP_value":tip["value"],"target":row["creator"]}
#         sp_graph = sp_graph.append(new_row, ignore_index=True)
# sp_graph.to_csv(r'main_datasets/splits_graph.csv')
# sp_graph.set_index(["source","target"],inplace=True)

# #auctions
# au = pd.read_csv(r'main_datasets/dune_data/mirror_au_all_graph.csv')
# au[["buyer","creator"]]=au[["buyer","creator"]].applymap(lambda x: x.replace("\\","0"))
# au_graph = au.pivot_table(index=["buyer","creator"],values="AU_value",aggfunc="sum")
# au_graph.index.names=["source","target"]
# au_graph.to_csv(r'main_datasets/auctions_graph.csv')

# ##add it all to consolidated df
# consolidated = consolidated.join(cf_graph,how="outer")
# consolidated = consolidated.join(ed_graph,how="outer")
# consolidated = consolidated.join(sp_graph,how="outer")
# consolidated = consolidated.join(au_graph,how="outer")

# """add in twitter data, this runs slowly lol"""
# print("getting twitter graph...")
# # #do we need to get the matrix of who has talked to who (co-occurence matrix)
# # from scipy.sparse import csr_matrix
# mdf = pd.read_csv(r'main_datasets\mirror_tw_mentionedby.csv', index_col=0)
# mdf.drop(columns="skipped_user", inplace=True)

# twitter_cols = ["source","mentions","target"]
# twitter_graph = pd.DataFrame(columns=twitter_cols)
# all_usernames_in_mirror = list(full_addy.username)

# for column in tqdm(mdf.columns):
#     all_mentions = mdf[column]
#     all_mentions.dropna(inplace=True)
#     for mention in all_mentions:
#         if mention in all_usernames_in_mirror:
#             new_mention = {"source":handle_eth[column.lower()], "mentions":1,"target":handle_eth[mention.lower()]}
#             twitter_graph = twitter_graph.append(new_mention, ignore_index=True)
            
# twitter_graph = twitter_graph.pivot_table(index=["source","target"],values="mentions", aggfunc="sum")
# twitter_graph.to_csv(r'main_datasets/twitter_graph.csv')

# consolidated = consolidated.join(twitter_graph,how="outer")

# consolidated.to_csv(r'main_datasets/mirror_graph_processed.csv')

"""graphing starts"""
import networkx as nx
import matplotlib.pyplot as plt
consolidated = pd.read_csv(r'main_datasets/mirror_graph_processed.csv', index_col=["source","target"])
consolidated_melt = consolidated.melt(ignore_index=False).dropna()

color_key = {"Votes":"black","mentions":"royalblue","CF_contribution":"rosybrown","ED_purchaseValue":"rosybrown","SP_value":"rosybrown","AU_value":"rosybrown"}
width_key = {"Votes":1,"mentions":1.5,"CF_contribution":2,"ED_purchaseValue":2,"SP_value":2,"AU_value":2}
alpha_key = {"Votes":1.0,"mentions":0.6,"CF_contribution":0.3,"ED_purchaseValue":0.3,"SP_value":0.3,"AU_value":0.3}

#use royalblue for twitter

consolidated_melt.reset_index(inplace=True)
G = nx.from_pandas_edgelist(consolidated_melt, "source","target", 
                            edge_key="variable", 
                            edge_attr=["value"],
                            create_using=nx.MultiGraph()) #digraph looks weird af, idk why. maybe better after removing self loops

#add in direction and color https://networkx.org/documentation/stable/reference/generated/networkx.convert_matrix.from_pandas_edgelist.html

#setting rules for color_map 
winners = pd.read_json(r'main_datasets\mirror_supplied\votingdata.json')
winners = list(set(winners[winners.hasPublication==True]["username"]))
winners_eth = [handle_eth[winner.lower()] for winner in winners]

color_map = []
for node in G:
    # print(node)
    if node in winners_eth:
        color_map.append("gold")
    else:
        color_map.append("indigo")

print("plotting graph...")
# labels = {addy:try_handle(addy) for addy in G.nodes()}

plt.figure(figsize=(50, 50))
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=10)
# nx.draw_networkx_labels(G,pos,labels,font_size=7,font_color='b')

for edge in color_key:
    nx.draw_networkx_edges(G, pos, connectionstyle='arc3, rad = 0.4',
        edgelist=consolidated_melt[consolidated_melt["variable"]==edge][["source","target"]].apply(tuple, axis=1),
        width=width_key[edge],
        alpha=alpha_key[edge],
        edge_color=color_key[edge])
    
plt.axis('off')
plt.show() 

# ###testing, seems multigraph doesn't support curved lines.
# edges = pd.DataFrame(
#     {
#         "source": [0, 1, 2, 0],
#         "target": [2, 2, 3, 2],
#         "my_edge_key": ["A", "B", "C", "D"],
#         "weight": [3, 4, 5, 6],
#         "color": ["red", "blue", "blue", "blue"],
#     }
# )
# G = nx.from_pandas_edgelist(
#     edges,
#     edge_key="my_edge_key",
#     edge_attr=["weight", "color"],
#     create_using=nx.MultiGraph(),
# )

# plt.figure(figsize=(50, 50))
# G = nx.MultiGraph()
# G.add_nodes_from([0,1,2,3])
# pos = nx.circular_layout(G)
# nx.draw_networkx_nodes(G, pos, node_color='blue', node_size=30)

# nx.draw_networkx_edges(G, pos, connectionstyle='arc3, rad = 0.1', edgelist = [(0,2)], width = 2, alpha = 0.5, edge_color='b')
# nx.draw_networkx_edges(G, pos, connectionstyle='arc3, rad = 0.1', edgelist= [(2,3)], width = 1, alpha = 1)

# # for edge in G.edges():
# #     attributes = G.get_edge_data(edge[0],edge[1])
# #     print("edge type: ", next(iter(attributes)))
# #     nx.draw_networkx_edges(G, pos, connectionstyle='arc3, rad = 0.4',
# #         edgelist=[edge],
# #         width=attributes[next(iter(attributes))]["weight"],
# #         alpha=0.5,
# #         edge_color=attributes[next(iter(attributes))]["color"])
    
# plt.axis('off')
# plt.show() 

# nx.write_gexf( G , r'main_datasets/social_graph.gexf' )

"""community graph analysis (uncomment only when you want to run the algos)"""
# from cdlib import algorithms
# coms = algorithms.louvain(G) 
# coms.average_internal_degree()
# coms.node_coverage
# com_ipca = algorithms.ipca(G)
# com_girvan = algorithms.girvan_newman(G, level=3)

# from cdlib import viz

# pos = nx.spring_layout(G) #look at more layouts later, I know there's a circle one and this one increases spread. 
# viz.plot_network_clusters(G, coms, pos, figsize=(30, 30),node_size=200, top_k=10) #for small clusters
# viz.plot_community_graph(G, coms, figsize=(6, 6), top_k=10) #for large ones

print("calculating closeness and betweenness...")
"""closeness"""
# closeness_h = nx.algorithms.centrality.harmonic_centrality(G) #not normalized
closeness_c = nx.algorithms.centrality.closeness_centrality(G) #normalized, uses WF formula

"""betweenness"""
# Generate connected components and select the largest:
largest_component = max(nx.connected_components(G), key=len)
# Create a subgraph of G consisting only of this component:
G2 = G.subgraph(largest_component)
# betweenness_nw= nx.algorithms.centrality.current_flow_betweenness_centrality(G2) #can be weighted... but I don't really understand this one
betweenness_c= nx.algorithms.centrality.betweenness_centrality_source(G2) 

"""putting into df"""
eth_handle = dict(zip(full_addy.address,full_addy.username))
def try_handle(x):
    try:
        return eth_handle[x]
    except:
        pass
    
def try_closeness(x):
    try:
        return closeness_c[x]
    except:
        return 1

def try_betweenness(x, betweenness):
    try:
        return betweenness[x]
    except:
        return betweenness[min(betweenness, key=betweenness.get)] #minimum value

consolidated_score = consolidated.reset_index().pivot_table(index=["source"],values=["Votes","CF_contribution","ED_purchaseValue","SP_value","AU_value","mentions"]
                                                            ,aggfunc="sum").reset_index()
consolidated_score["twitter"] = consolidated_score["source"].apply(lambda x: try_handle(x))
consolidated_score["hasVoted"] = consolidated_score["twitter"].apply(lambda x: 1 if x != np.nan else 0)

consolidated_score["closeness"] = consolidated_score["source"].apply(lambda x: try_closeness(x))
consolidated_score["betweenness"] = consolidated_score["source"].apply(lambda x: try_betweenness(x, betweenness_c))
consolidated_score["betweenness"] = consolidated_score["betweenness"] - min(consolidated_score["betweenness"]) #must be base 0

print("saved!")
consolidated_score.to_csv(r'main_datasets\mirror_graph_score_ready.csv')

##make venn diag on how many people mentioned, voted, and contributed to each other overlap. This could deff be refactored hahaha
from matplotlib_venn import venn3

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

venn3(subsets = (total_voters, total_twitters, total_voters_twitters, total_funders, total_voters_funders, total_funders_twitters, total_funders_twitters_voters), 
      set_labels = ('$WRITE Race', 'Twitter', 'Contributors (Ethereum Txs)'), set_colors=('r', 'g', 'b'), alpha = 0.5);
