# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 18:15:56 2021

@author: Andrew
"""

import pandas as pd
from tqdm import tqdm
"""changing of json into source-target format"""
# df = pd.read_json(r'main_datasets\votingdata.json')

# vote_graph = pd.DataFrame(columns=["Voter","Votes","Voted"])

# for index, row in tqdm(df.iterrows()):
#     for backer in row["backers"]:
#         new_row = {"Voter":backer["username"],"Votes":backer["amount"],"Voted":row["username"]}
#         vote_graph = vote_graph.append(new_row, ignore_index=True)
        
# len(set(vote_graph["Voter"])) #only 2041 out of 7000 handle have voted?

# vote_graph.to_csv(r'main_datasets\voting_graph_full.csv')

"""
network graph, multi directional

https://towardsdatascience.com/customizing-networkx-graphs-f80b4e69bedf

"""
import networkx as nx
from sklearn import preprocessing
votes = pd.read_csv(r'main_datasets\voting_graph_full.csv', index_col=0)
#len(set(df["Voter"].append(df["Voted"]))) 2130 nodes total
votes = votes[votes["Voter"]!=votes["Voted"]] #remove those who voted for self

#this should be the only place ethereum to twitter address is used
full_addy = pd.read_csv(r'main_datasets/mirror_tv.csv', index_col=0)
# verified_num = full_addy.pivot_table(index="username", values="address", aggfunc="count")
full_addy = full_addy.drop_duplicates(subset="username",keep="first") #this is REALLY important since some users have verified more than once, but the votes json file registers only their first signed address
full_addy.address = full_addy.address.apply(lambda x: x.lower())
handle_eth = dict(zip(full_addy.username,full_addy.address))

votes["Voter"] = votes["Voter"].apply(lambda x: handle_eth[x])
votes["Voted"] = votes["Voted"].apply(lambda x: handle_eth[x])

consolidated = votes.pivot_table(index=["Voter","Voted"], values="Votes", aggfunc="sum")
consolidated.index.names=["source","target"]

#add in ethereum graphs, no need to convert since this is base node.
cf = pd.read_csv(r'main_datasets\dune_data\mirror_cf_contonly.csv', index_col=0)
ed = pd.read_csv(r'main_datasets\dune_data\mirror_ed_graph.csv')

cf_cons = cf.pivot_table(index=["contributor","creator"],values="contribution",aggfunc="sum")
cf_cons.index.names=["source","target"]
cf_cons.columns=["CF_contribution"]
cf_cons["CF_contribution"] = cf_cons["CF_contribution"].div(1e18)

ed_cons = ed.pivot_table(index=["buyer","seller"],values="valuebought",aggfunc="sum")
ed_cons.index.names=["source","target"]
ed_cons.columns=["ED_purchaseValue"]

consolidated = consolidated.join(cf_cons,how="outer")
consolidated = consolidated.join(ed_cons,how="outer")

##only 40 people voted and contributed to same person
# consolidated.reset_index(inplace=True)
# consolidated["twitter_source"] = consolidated["source"].apply(lambda x: try_handle(x))
# consolidated["twitter_target"] = consolidated["target"].apply(lambda x: try_handle(x))
# testing = consolidated[(consolidated["Votes"]>=0) & ((consolidated["CF_contribution"]>=0) | (consolidated["ED_purchaseValue"]>=0))]

#add in twitter graphs, converted to ethereum addresses. 






"""graphing starts"""
import matplotlib.pyplot as plt
consolidated_melt = consolidated.melt(ignore_index=False).dropna()

color_key = {"Votes":"black","CF_contribution":"red","ED_purchaseValue":"red"}
width_key = {"Votes":1,"CF_contribution":2,"ED_purchaseValue":2}
alpha_key = {"Votes":1.0,"CF_contribution":0.5,"ED_purchaseValue":0.5}

consolidated_melt.reset_index(inplace=True)
G = nx.from_pandas_edgelist(consolidated_melt, "source","target", 
                            edge_key="variable", 
                            edge_attr=["value"],
                            create_using=nx.MultiGraph()) #digraph looks weird af, idk why. maybe better after removing self loops

#add in direction and color https://networkx.org/documentation/stable/reference/generated/networkx.convert_matrix.from_pandas_edgelist.html

#setting rules for color_map 
winners = pd.read_json(r'main_datasets\votingdata.json')
winners = list(set(winners[winners.hasPublication==True]["username"]))
winners_eth = [handle_eth[winner] for winner in winners]

color_map = []
for node in G:
    # print(node)
    if node in winners_eth:
        color_map.append("green")
    else:
        color_map.append("blue")

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

"""community graph analysis (uncomment only when you want to run the algos)"""
# # from cdlib import algorithms
# # coms = algorithms.louvain(G) 
# # coms.average_internal_degree()
# # coms.node_coverage
# # com_ipca = algorithms.ipca(G)
# # com_girvan = algorithms.girvan_newman(G, level=3)

# # from cdlib import viz

# # pos = nx.spring_layout(G) #look at more layouts later, I know there's a circle one and this one increases spread. 
# # viz.plot_network_clusters(G, coms, pos, figsize=(30, 30),node_size=200, top_k=10) #for small clusters
# # viz.plot_community_graph(G, coms, figsize=(6, 6), top_k=10) #for large ones

# """closeness"""
# # closeness_h = nx.algorithms.centrality.harmonic_centrality(G) #not normalized
# closeness_c = nx.algorithms.centrality.closeness_centrality(G) #normalized, uses WF formula

# """betweenness"""
# # Generate connected components and select the largest:
# largest_component = max(nx.connected_components(G), key=len)
# # Create a subgraph of G consisting only of this component:
# G2 = G.subgraph(largest_component)
# # betweenness_nw= nx.algorithms.centrality.current_flow_betweenness_centrality(G2) #can be weighted... but I don't really understand this one
# betweenness_c= nx.algorithms.centrality.betweenness_centrality_source(G2) 

# """putting into df"""
# eth_handle = dict(zip(full_addy.address,full_addy.username))
# def try_handle(x):
#     try:
#         return eth_handle[x]
#     except:
#         return x
    
# def try_closeness(x):
#     try:
#         return closeness_c[x]
#     except:
#         return 1

# def try_betweenness(x, betweenness):
#     try:
#         return betweenness[x]
#     except:
#         return betweenness[min(betweenness, key=betweenness.get)] #minimum value

# consolidated_df = consolidated.reset_index().pivot_table(index=["source"],values=["Votes","CF_contribution","ED_purchaseValue"],aggfunc="sum").reset_index()
# consolidated_df["twitter"] = consolidated_df["source"].apply(lambda x: try_handle(x))
# consolidated_df["closeness"] = consolidated_df["source"].apply(lambda x: try_closeness(x))
# consolidated_df["betweenness"] = consolidated_df["source"].apply(lambda x: try_betweenness(x, betweenness_c))
# consolidated_df["betweenness"] = consolidated_df["betweenness"] - min(consolidated_df["betweenness"]) #must be base 0

# consolidated_df.to_csv(r'main_datasets\mirror_graph_score_ready.csv')