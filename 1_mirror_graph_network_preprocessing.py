# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 22:10:56 2021

@author: Andrew
"""

import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn import preprocessing

print("starting preprocessing...")
# df = pd.read_json(r'main_datasets\votingdata.json')

# vote_graph = pd.DataFrame(columns=["Voter","Votes","Voted"])

# for index, row in tqdm(df.iterrows()):
#     for backer in row["backers"]:
#         new_row = {"Voter":backer["username"],"Votes":backer["amount"],"Voted":row["username"]}
#         vote_graph = vote_graph.append(new_row, ignore_index=True)
        
# len(set(vote_graph["Voter"])) #only 2041 out of 7000 handle have voted?

# vote_graph.to_csv(r'main_datasets/graph_data/voting_graph_full.csv')

votes = pd.read_csv(r'main_datasets/graph_data/voting_graph_full.csv', index_col=0)
votes = votes[votes["Votes"]!=0] #seems like some error in the json file
#len(set(df["Voter"].append(df["Voted"]))) 2130 nodes total
votes = votes[votes["Voter"]!=votes["Voted"]] #remove those who voted for self

full_addy = pd.read_csv(r'main_datasets/mirror_supplied/mirror_tv.csv', index_col=0)
# verified_num = full_addy.pivot_table(index="username", values="address", aggfunc="count")
full_addy = full_addy.drop_duplicates(subset="username",keep="first") #this is REALLY important since some users have verified more than once, but the votes json file registers only their first signed address
full_addy.address = full_addy.address.apply(lambda x: x.lower())
full_addy.username = full_addy.username.apply(lambda x: x.lower())
handle_eth = dict(zip(full_addy.username,full_addy.address))
votes[["Voter","Voted"]] = votes[["Voter","Voted"]].applymap(lambda x: handle_eth[x.lower()])

"""

add in ethereum transaction data to graph network and save file as consolidated

"""

graph_all = pd.read_csv(r'main_datasets\dune_data\mirror_all_graph.csv')
graph_all = graph_all[graph_all["contribution"]!=0] #filter this out from query later

consolidated = votes.pivot_table(index=["Voter","Voted"], values="Votes", aggfunc="sum")
consolidated.index.names=["source","target"]

#crowdfunds
cf = graph_all[graph_all["product_type"]=="crowdfund"]

#3 creators are missing from dune logs for some reason
missing_cf_creator = {'\\x41ed7d49292b8fbf9b9311c1cb4d6eb877646c58':'0x48A63097E1Ac123b1f5A8bbfFafA4afa8192FaB0', 
                    '\\xa338f6960d1e8bcde50a8057173229dcaa4428c9':'0xA0Cf798816D4b9b9866b5330EEa46a18382f251e',
                    '\\x94515e4f6fabad73c8bcdd8cd42f0b5c037e2c49': '0xc3268ddb8e38302763ffdc9191fcebd4c948fe1b'}

def fill_missing_cf_creators(x):
    try:
        return missing_cf_creator[x]
    except:
        return x

cf["creator"] = cf["contract_address"].apply(lambda x: fill_missing_cf_creators(x)) 
cf[["buyer","contract_address","creator"]]=cf[["buyer","contract_address","creator"]].applymap(lambda x: x.replace("\\","0"))
cf_graph = cf.pivot_table(index=["buyer","creator"],values="contribution",aggfunc="sum")
cf_graph.index.names=["source","target"]
cf_graph.columns=["CF_contribution"]
cf_graph.to_csv(r'main_datasets/graph_data/crowdfunds_graph.csv')

#editions
ed = graph_all[graph_all["product_type"]=="editions"]
ed_graph = ed.pivot_table(index=["buyer","creator"],values="contribution",aggfunc="sum")
ed_graph.index.names=["source","target"]
ed_graph.columns=["ED_purchaseValue"]
ed_graph.to_csv(r'main_datasets/graph_data/editions_graph.csv')

#splits --will have to drop all that are 0 value
sp = graph_all[graph_all["product_type"]=="splits"]
sp_graph = sp.pivot_table(index=["buyer","creator"],values="contribution",aggfunc="sum")
sp_graph.index.names=["source","target"]
sp_graph.columns=["SP_value"]
sp_graph.to_csv(r'main_datasets/graph_data/splits_graph.csv')

#auctions
au = graph_all[graph_all["product_type"]=="reserve_auctions"]
au[["buyer","creator"]]=au[["buyer","creator"]].applymap(lambda x: x.replace("\\","0"))
au_graph = au.pivot_table(index=["buyer","creator"],values="contribution",aggfunc="sum")
au_graph.index.names=["source","target"]
au_graph.columns=["AU_value"]
au_graph.to_csv(r'main_datasets/graph_data/auctions_graph.csv')

##add it all to consolidated df
consolidated = consolidated.join(cf_graph,how="outer")
consolidated = consolidated.join(ed_graph,how="outer")
consolidated = consolidated.join(sp_graph,how="outer")
consolidated = consolidated.join(au_graph,how="outer")

"""add in twitter data, this runs slowly lol. this should work with every single user"""
# print("getting twitter graph...")
# # #do we need to get the matrix of who has talked to who (co-occurence matrix)
# # from scipy.sparse import csr_matrix
# mdf = pd.read_csv(r'main_datasets\mirror_tw_mentionedby.csv', index_col=0)
# mdf.drop(columns="skipped_user", inplace=True)
# mdf_2 = pd.read_csv(r'main_datasets\mirror_tw_mentionedby_all.csv', index_col=0)
# mdf_2.drop(columns="skipped_user", inplace=True)

# mdf = pd.concat([mdf,mdf_2])

# twitter_cols = ["source","mentions","target"]
# twitter_graph = pd.DataFrame(columns=twitter_cols)
# all_usernames_in_mirror = list(full_addy.username)

# for column in tqdm(mdf.columns):
#     all_mentions = mdf[column]
#     all_mentions.dropna(inplace=True)
#     if column in all_usernames_in_mirror: #remove this later
#         for mention in all_mentions:
#             if (mention in all_usernames_in_mirror) & (column != mention):
#                 new_mention = {"source":handle_eth[column.lower()], "mentions":1,"target":handle_eth[mention.lower()]}
#                 twitter_graph = twitter_graph.append(new_mention, ignore_index=True)
            
# twitter_graph = twitter_graph.pivot_table(index=["source","target"],values="mentions", aggfunc="sum")
# twitter_graph.to_csv(r'main_datasets/graph_data/twitter_graph.csv')

twitter_graph = pd.read_csv(r'main_datasets/graph_data/twitter_graph.csv', index_col=["source","target"])

consolidated = consolidated.join(twitter_graph,how="outer")

"""save down"""
consolidated.to_csv(r'main_datasets/mirror_graph_processed.csv')
