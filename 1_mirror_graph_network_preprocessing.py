# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 22:10:56 2021

@author: Andrew
"""

import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn import preprocessing

print("starting preprocessing... remember to uncomment section if new voting graph")
# votesjson = pd.read_json(r'main_datasets\mirror_supplied\votingdata.json')

# vote_graph = pd.DataFrame(columns=["Voter","Votes","Voted"])

# for index, row in tqdm(votesjson.iterrows()):
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
graph_all = graph_all[graph_all["contribution"]!=0] #filter this out from query 
graph_all.dropna(inplace=True) #some cf didn't get any contributions
graph_all[["buyer","contract_address","creator"]]=graph_all[["buyer","contract_address","creator"]].applymap(lambda x: x.replace("\\","0"))

consolidated = votes.pivot_table(index=["Voter","Voted"], values="Votes", aggfunc="sum")
consolidated.index.names=["source","target"]

#crowdfunds
cf = graph_all[graph_all["product_type"]=="crowdfund"]

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

"""add in votes percentage data"""
votesjson = pd.read_json(r'main_datasets\mirror_supplied\votingdata.json')
votes = pd.read_csv(r'main_datasets/graph_data/voting_graph_full.csv', index_col=0)
votes_given = votes.pivot_table(index="Voter",values="Votes",aggfunc="sum") #for calculation later
votes_given = votes_given.reset_index()

votes_giversonly = votesjson[votesjson["username"].isin(set(votes_given["Voter"]))][["username","originalVotingPower"]]
votes_giversonly.columns=["Voter","Votes_Allocated"]

somehow_missing = set(votes_given["Voter"]) -set(votes_giversonly["Voter"]) 
for missing in somehow_missing:
    votes_given_by_missing = votes_given[votes_given["Voter"]==missing]["Votes"].reset_index(drop=True)[0]
    #this is rough estimate, could be wrong.
    votes_allocated = 10 if votes_given_by_missing <= 10 else round(votes_given_by_missing/10)*10
    append_missing = {"Voter": missing, "Votes_Allocated": votes_allocated}
    votes_giversonly = votes_giversonly.append(append_missing, ignore_index=True)
    
allocated = pd.read_excel(r'main_datasets/mirror_supplied/mirror_leaderboard.xlsx')
allocated_dict = dict(zip(allocated.winner,allocated.allocation))

def try_add_allocate(x):
    try:
        return allocated_dict[x]
    except:
        return 0 

votes_giversonly["allocated_additional"] = votes_giversonly["Voter"].apply(lambda x: try_add_allocate(x))
votes_giversonly["Votes_Allocated"] = votes_giversonly["Votes_Allocated"] + votes_giversonly["allocated_additional"]

merged_votes = pd.merge(votes_given, votes_giversonly, how="left", on="Voter")

#getting above 100%
merged_votes["percentage_votes_used"] = merged_votes["Votes"].div(merged_votes["Votes_Allocated"])

merged_votes["Voter"] = merged_votes["Voter"].apply(lambda x: handle_eth[x.lower()])
percentage_allocated_dict = dict(zip(merged_votes.Voter,merged_votes.percentage_votes_used))

def set_merge_percent_allocate(x):
    try:
        return percentage_allocated_dict[x]
    except:
        return 0

consolidated.reset_index(inplace=True)
consolidated["percentage_votes_used"] = consolidated.source.apply(lambda x: set_merge_percent_allocate(x))
consolidated.set_index(["source","target"], inplace=True)

"""save down"""
consolidated.to_csv(r'main_datasets/mirror_graph_processed.csv')
