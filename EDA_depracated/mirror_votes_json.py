# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 18:15:56 2021

@author: Andrew
"""

import pandas as pd
from tqdm import tqdm

"""changing of json into source-target format"""
# df = pd.read_json(r'C:\Users\Andrew\OneDrive - nyu.edu\Documents\Python Script Backup\datasets\votingdata.json')

# vote_graph = pd.DataFrame(columns=["Voter","Votes","Voted"])

# for index, row in tqdm(df.iterrows()):
#     for backer in row["backers"]:
#         new_row = {"Voter":backer["username"],"Votes":backer["amount"],"Voted":row["username"]}
#         vote_graph = vote_graph.append(new_row, ignore_index=True)
        
# len(set(vote_graph["Voter"])) #only 2041 out of 7000 handle have voted?

# vote_graph.to_csv(r'C:\Users\Andrew\OneDrive - nyu.edu\Documents\Python Script Backup\datasets\voting_graph_full.csv')

"""
network graph
https://towardsdatascience.com/customizing-networkx-graphs-f80b4e69bedf
"""
import networkx as nx
from sklearn import preprocessing
df = pd.read_csv(r'C:\Users\Andrew\OneDrive - nyu.edu\Documents\Python Script Backup\datasets\voting_graph_full.csv', index_col=0)
#len(set(df["Voter"].append(df["Voted"]))) 2130 nodes total

full_addy = pd.read_csv(r'C:/Users/Andrew/OneDrive - nyu.edu/Documents/Python Script Backup/datasets/mirror_tv.csv', index_col=0)
full_addy.address = full_addy.address.apply(lambda x: x.lower())
handle_eth = dict(zip(full_addy.username,full_addy.address))
df["Voter"] = df["Voter"].apply(lambda x: handle_eth[x])
df["Voted"] = df["Voted"].apply(lambda x: handle_eth[x])

winners = pd.read_json(r'C:\Users\Andrew\OneDrive - nyu.edu\Documents\Python Script Backup\datasets\votingdata.json')
winners = list(set(winners[winners.hasPublication==True]["username"]))
winners_eth = [handle_eth[winner] for winner in winners]

#calculations for sizemapping
votes_given = df.pivot_table(index="Voter", values="Votes", aggfunc="sum").reset_index()
min_max_scaler = preprocessing.MinMaxScaler()
votes_given["scaled_votes"] = min_max_scaler.fit_transform(votes_given[["Votes"]]) + 0.01
votes_given["scaled_votes"]= votes_given["scaled_votes"]*2000
scaled_votes_dict = dict(zip(votes_given.Voter,votes_given.scaled_votes))

#add in ethereum graphs, no need to convert since this is base node.
cf = pd.read_csv(r'C:\Users\Andrew\OneDrive - nyu.edu\Documents\Python Script Backup\datasets\dune_scrapes\mirror_cf_contonly.csv', index_col=0)
ed = pd.read_csv(r'C:\Users\Andrew\OneDrive - nyu.edu\Documents\Python Script Backup\datasets\dune_scrapes\mirror_ed_graph.csv')

#add in twitter graphs, converted to ethereum addresses. 


#graphing starts
G = nx.from_pandas_edgelist(df, 'Voter', 'Voted', ['Votes']) 
#add in direction and color https://networkx.org/documentation/stable/reference/generated/networkx.convert_matrix.from_pandas_edgelist.html

color_map = []
for node in G:
    if node in winners_eth:
        color_map.append("green")
    else:
        color_map.append("blue")

size_map = []
for node in G:
    try:
        size_map.append(scaled_votes_dict[node])
    except KeyError:
        size_map.append(votes_given["scaled_votes"].min()) #this was someone who didn't vote once but was voted for.

from matplotlib.pyplot import figure
figure(figsize=(50, 50))
nx.draw_networkx(G, node_color=color_map, node_size=size_map, with_labels=False) #arrows don't show up?

"""graph analysis"""
# from cdlib import algorithms
# #how to enable directional?
# coms = algorithms.louvain(G) #which algorithms allow for overlap? how to shade the overlap?
# coms.communities
# coms.average_internal_degree()
# coms.node_coverage

# from cdlib import viz

# pos = nx.spring_layout(G) #look at more layouts later, I know there's a circle one and this one increases spread. 
# viz.plot_network_clusters(G, coms, pos, figsize=(30, 30),node_size=200, top_k=10) #for small clusters
# viz.plot_community_graph(G, coms, figsize=(6, 6), top_k=10) #for large ones

# import itertools
# # for if manual removal is warranted, must run graph analysis below first
# top_communities = list(itertools.chain.from_iterable(coms.communities[:10])) 
# remove = [node for node in G if node not in top_communities]
# G.remove_nodes_from(remove)