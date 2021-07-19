# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 13:57:20 2021

@author: Andrew
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
sns.set_theme()

df = pd.read_csv(r'C:/Users/Andrew/OneDrive - nyu.edu/Documents/Python Script Backup/datasets/mirror_leaders_waddresses.csv', index_col=0)
#may want to update this with new vote set to add in 

###for twitter thread
#get number of votes for winners each round/overlapping distribution? # of voters to win, concentration of votes to win
pivot_votes = df.pivot_table(index=["Round","Username"],values="Total_Votes",aggfunc="mean").reset_index()
f, ax = plt.subplots(figsize=(9, 6))
sns.boxplot(x="Round", y="Total_Votes", data=pivot_votes, ax=ax)
ax.set(title="$WRITE Round Winner Vote Distribution")

#get most active voters by # of total votes given
pivot_vote_from = df.pivot_table(index="Vote_From",values="Vote_Amount",aggfunc="sum").reset_index()
pivot_vote_from = pivot_vote_from.sort_values(by="Vote_Amount", ascending=False)
f, ax = plt.subplots(figsize=(8, 12))
sns.barplot(x="Vote_Amount", y="Vote_From", data=pivot_vote_from.iloc[:20,:], ax=ax)
ax.set(title="Total Votes By User Across All Rounds (To Winners)")

#get most active voters by # of different people supported 
pivot_vote_from = df.pivot_table(index="Vote_From",values="Vote_Amount",aggfunc="count").reset_index()
pivot_vote_from = pivot_vote_from.sort_values(by="Vote_Amount", ascending=False)
f, ax = plt.subplots(figsize=(8, 12))
sns.barplot(x="Vote_Amount", y="Vote_From", data=pivot_vote_from.iloc[:20,:], ax=ax)
ax.set(title="Total Unique Writers Voted For By User Across All Rounds (To Winners)")

#heatmap of round votes/voters
round_winner = df[["Round","Username"]].drop_duplicates()
round_winner.columns = ["Won_Round","Vote_From"]
round_joined = pd.merge(df,round_winner, on="Vote_From",how="left")
round_joined = round_joined[round_joined["Won_Round"].notna()]
pivot_round_to = round_joined.pivot_table(index="Won_Round",columns="Round",values="Vote_Amount",aggfunc="sum").fillna(0)
pivot_round_to.reset_index(inplace=True, drop=True)

f, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot_round_to, linewidths=.8, cmap = "Blues", ax=ax)
ax.set(title="Contribution of Votes from Past Winners (Y-axis) to Current Winners (X-axis) by Round"
        ,xlabel="Current Round Winners"
        ,ylabel="Votes by Past Round Winners")

#heatmap of round votes/voters as a percent
round_winner = df[["Round","Username"]].drop_duplicates()
round_winner.columns = ["Won_Round","Vote_From"]

round_winner_total_votes = round_winner.pivot_table(index="Won_Round",values="Vote_From",aggfunc="count")
round_winner_total_votes.columns = ["Available_Votes"]
round_winner_total_votes["Available_Votes"] = round_winner_total_votes["Available_Votes"].apply(lambda x: x*1000) #1000 votes per winner

round_joined = pd.merge(df,round_winner, on="Vote_From",how="left")
round_joined = round_joined[round_joined["Won_Round"].notna()]
pivot_round_to = round_joined.pivot_table(index="Won_Round",columns="Round",values="Vote_Amount",aggfunc="sum").fillna(0)
pivot_round_to = pivot_round_to.div(round_winner_total_votes["Available_Votes"], axis=0).mul(100)
pivot_round_to.reset_index(inplace=True, drop=True)

f, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(pivot_round_to, linewidths=.8, cmap = "Blues", ax=ax)
ax.set(title="Contribution of Votes from Past Winners (Y-axis) to Current Winners (X-axis) by Round Divided by Total Available Votes"
        ,xlabel="Current Round Winners"
        ,ylabel="Votes by Past Round Winners")

#heatmap of round votes/voters as a cumulative percent
cumulative_avail_votes = round_winner_total_votes.cumsum()
pivot_round_to = round_joined.pivot_table(index="Won_Round",columns="Round",values="Vote_Amount",aggfunc="sum").fillna(0)
pivot_round_to_all = pivot_round_to.sum(axis=0)
pivot_round_to_all_percent = pivot_round_to_all.div(cumulative_avail_votes["Available_Votes"].shift(1)[1:], axis=0).reset_index()
f, ax = plt.subplots(figsize=(12, 8))
sns.barplot(x="Round", y=0, data=pivot_round_to_all_percent, ax=ax, palette=["lightgreen"])
ax.set(title="Appx. Percentage of Total Available Votes Allocated to Each Round (From Winners)"
        ,xlabel="Current Round Winners"
        ,ylabel="Votes by Past Round Winners")

###future
#who has or hasn't created an ENS after winning (done)
#then need ethereum address data and crowdfund/edition data (half done, do analysis in different file)

