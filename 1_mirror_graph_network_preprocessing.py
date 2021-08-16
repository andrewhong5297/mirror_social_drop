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

###we could use timestamped votes for this, but there are some missing twitter verifs to account for. votes.json is a cleaner file.
# votesjson = pd.read_json(r'main_datasets\mirror_supplied\votes.json')

# vote_graph = pd.DataFrame(columns=["Voter","Votes","Voted"])

# for index, row in tqdm(votesjson.iterrows()):
#     for backer in row["backers"]:
#         new_row = {"Voter":backer["username"],"Votes":backer["amount"],"Voted":row["username"]}
#         vote_graph = vote_graph.append(new_row, ignore_index=True)
        
# len(set(vote_graph["Voter"])) 

# vote_graph.to_csv(r'main_datasets/graph_data/voting_graph_full.csv')

votes = pd.read_csv(r'main_datasets/graph_data/voting_graph_full.csv', index_col=0)

votes = votes[votes["Votes"]!=0] #seems like some error in the json file
#len(set(df["Voter"].append(df["Voted"])))
votes = votes[votes["Voter"]!=votes["Voted"]] #remove those who voted for self

full_addy = pd.read_csv(r'main_datasets/mirror_supplied/TwitterVerifications.csv', index_col=0)
full_addy = full_addy.drop_duplicates(subset="username",keep="first") #this is REALLY important since some users have verified more than once, but the votes json file registers only their first signed address
full_addy.account = full_addy.account.apply(lambda x: x.lower())
full_addy.username = full_addy.username.apply(lambda x: x.lower())
handle_eth = dict(zip(full_addy.username,full_addy.account))
eth_handle = dict(zip(full_addy.account,full_addy.username))

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

"""

add in twitter data, this runs slowly lol. this should work with every single user

"""
print("getting twitter graph...")
# # #do we need to get the matrix of who has talked to who (co-occurence matrix)
# # from scipy.sparse import csr_matrix
# mdf = pd.read_csv(r'main_datasets\mirror_tw_mentionedby_08122021_full.csv', index_col=0)
# mdf.drop(columns="skipped_user", inplace=True)

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
# twitter_graph.to_csv(r'main_datasets/graph_data/twitter_graph_final.csv')

twitter_graph = pd.read_csv(r'main_datasets/graph_data/twitter_graph_final.csv', index_col=["source","target"])

consolidated = consolidated.join(twitter_graph,how="outer")

"""

add in votes percentage used out of allocated. gets complex because allocated is available weekly

"""
votes_timestamped = pd.read_csv(r'main_datasets/mirror_supplied/InvitationVotes.csv')
votes_timestamped = votes_timestamped.drop_duplicates(subset=["candidate","account","signature","round","amount"])
votes_timestamped.rename(columns={"account":"Voter", "amount":"Votes", "candidate":"Voted"}, inplace=True)

votes_timestamped["Voter"] = votes_timestamped["Voter"].apply(lambda x: x.lower())
# votes_given_ts = votes_timestamped.pivot_table(index=["account","candidate"],values="amount",aggfunc="sum") #refactor code with this above later for voter_graph later
votes_given = votes_timestamped.pivot_table(index="Voter",values="Votes",aggfunc="sum")
votes_given.reset_index(inplace=True)
votes_given["Votes_Allocated"] = 10 #everyone starts with 10 votes, then we add on allocation from leaderboard and also from votes_timestamped

#add new votes allocated_weekly
votes_weekly = votes_timestamped.pivot_table(index="Voter",columns="round", values="Votes", aggfunc="sum")
votes_weekly[~votes_weekly.isnull()] = 10
votes_weekly.fillna(0,inplace=True)
votes_weekly = votes_weekly.cumsum(axis=1)
votes_weekly["total_votes_allocated"] = votes_weekly.sum(axis=1)

votes_given = pd.merge(votes_given,votes_weekly.reset_index()[["Voter","total_votes_allocated"]],on="Voter",how="left")

#add on winners allocation weekly
allocated = pd.read_excel(r'main_datasets/mirror_supplied/mirror_leaderboard.xlsx') #this is a manual input spreadsheet
allocated["winner"] = allocated["winner"].apply(lambda x: handle_eth[x.lower()])
allocated_dict = dict(zip(allocated.winner,allocated.allocation))

def try_add_allocate(x):
    try:
        return allocated_dict[x]
    except:
        if x == "0x4c0a466df0628fe8699051b3ac6506653191cc21":
            return 22000 #manual for duplicate, probably lost on merge anyways.
        return 0 

votes_given["allocated_additional_winners"] = votes_given["Voter"].apply(lambda x: try_add_allocate(x))

#sum up all additional votes
votes_given["Votes_Allocated"] = votes_given["Votes_Allocated"] + votes_given["allocated_additional_winners"] + votes_given["total_votes_allocated"]

#take percentage of votes/votes_allocated
votes_given["percentage_votes_used"] = votes_given["Votes"].div(votes_given["Votes_Allocated"])

percentage_allocated_dict = dict(zip(votes_given.Voter,votes_given.percentage_votes_used))

#assign percentages back to consolidated. Could have done a join then fillna with 0 I guess, but this is pretty fast. 
def set_merge_percent_allocate(x):
    try:
        percentage = percentage_allocated_dict[x] 
        if percentage > 1.5:
            return 0 #there are some bots that were removed
        if percentage > 1:
            return 1 #there are maybe 10-20 votes missed for a few people in early rounds
        else:
            return percentage
    except:
        return 0

consolidated.reset_index(inplace=True)
consolidated["percentage_votes_used"] = consolidated.source.apply(lambda x: set_merge_percent_allocate(x))
consolidated.set_index(["source","target"], inplace=True)

"""

save down

"""
consolidated.to_csv(r'main_datasets/mirror_graph_processed.csv')
