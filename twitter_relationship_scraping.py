# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 10:06:19 2021

@author: Andrew
"""

import tweepy
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
from tqdm import tqdm

#refactor this later for if more usernames are added
all_users = pd.read_json(r'main_datasets\mirror_supplied\votingdata.json')
active_users = pd.read_csv(r'main_datasets\graph_data\voting_graph_full.csv', index_col=0)
users_already_scraped = list(set(active_users["Voter"].append(active_users["Voted"])))
users_to_scrape = set(all_users["username"]) - set(active_users["Voter"].append(active_users["Voted"]))
users = list(users_to_scrape)

###setting up twitter api
consumer_key = "YqBOnr9To6U1ItTMWr5emdGjE" #dKJE1GlWlnXXdoEh9X706PifF
consumer_secret = "DMcdKA9hAP5il1blT2sKZMowBYG5uiKvOxihZKeB7Xw2uzQQLk" #26qyIASFEQnUENgseZHLkczNW6aZgSrOZ7UhnDoY9R8Nn0kTJ9
access_token = "801246156340740096-eNUEV9IyTsPE0aPuwGpG52S9gVjAzzI"
access_token_secret = "sdq7i2lqRCAEiEYyoX32enxgGtUgJZLmkr02et541YbkF"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)

#mentions by a user
mdf = pd.read_csv(r'main_datasets\mirror_tw_mentionedby_all.csv', index_col=0)
mentioned_by = mdf.to_dict(orient="list")
# mentioned_by = {}
for user in tqdm(users[len(mentioned_by):]):
    # print(user, datetime.now())
    if user in mentioned_by:
        pass
    else:
        try:
            tweet_temp = tweepy.Cursor(api.user_timeline,id=user).items(2000)
            mentions_temp = [mentioned[0]["screen_name"] if len(mentioned)>0 else np.nan for mentioned in [tweet.entities["user_mentions"] for tweet in tweet_temp]]
            mentioned_by[user] = pd.Series(mentions_temp).dropna()
        except:
            #sometimes you end up with 401/404 errors when searching up a twitter handle, it might be deleted or private
            if "skipped_user" not in mentioned_by:
                mentioned_by["skipped_user"] = user
            else:
                current_skips = mentioned_by["skipped_user"]
                if isinstance(current_skips, str):
                    current_skips = [current_skips, user]
                else:
                    current_skips.append(user)
                mentioned_by["skipped_user"] = current_skips
        mdf = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in mentioned_by.items() ]))
        #SAVE AS CSV AS YOU GO
        mdf.to_csv(r'main_datasets\mirror_tw_mentionedby_all.csv')

### below all take too long
# # favorites for a given user
# fvdf = pd.read_csv(r'main_datasets\mirror_tw_favorites.csv', index_col=0)
# favorites = fvdf.to_dict(orient="list")
# for user in users[len(favorites):]:
#     print(user, datetime.now())
#     if user in favorites or user=="Crept89454536":
#         pass
#     else:
#         favorites_temp = tweepy.Cursor(api.favorites,id=user).items()
#         favorites[user] = [favorite.user.screen_name for favorite in favorites_temp]
#         fvdf = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in favorites.items() ]))
#         #SAVE AS CSV AS YOU GO
#         fvdf.to_csv(r'main_datasets\mirror_tw_favorites.csv')

# # get followers, then get matrix of who follows who. Save followers down though so we don't have to re-scrape. 
# followers = {}
# for user in users:
#     print(user, datetime.now())
# if user in followers:
#         pass
#     else:
#     follow_temp = tweepy.Cursor(api.followers,id=user).items()
#     followers[user] = [follower.screen_name for follower in follow_temp]
#     fdf = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in followers.items() ]))
#     #SAVE AS CSV AS YOU GO
#     fdf.to_csv(r'main_datasets\mirror_tw_followers.csv')
    
# retweeters for a given tweet id
# replies for a given tweet id

##testing
# favorites_temp = tweepy.Cursor(api.favorites,id="andrewhong5297").items(10)
# favorites["andrewhong5297"] = [favorite for favorite in favorites_temp]