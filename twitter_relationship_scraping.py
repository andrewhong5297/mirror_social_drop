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
all_users = pd.read_json(r'main_datasets\mirror_supplied\votes.json')
users = list(set(all_users["username"]))

###setting up twitter api
consumer_key ="3EKL6CHHdbs8Su04Fwr3Ja4He"
consumer_secret = "epTy2J7hsgZ2rqDypDfC2Eudz9le3sL4N3xr2Oc4aT8WXxAkmv"
access_token = "801246156340740096-gBQRqQvzWrMdob8bK8YlJIKzRrQ1uHX"
access_token_secret = "nd2ImDF79d4Rd81r87VMBeBi1RPmwfGBNKYyyAzIwXXla" 

# consumer_key ="YqBOnr9To6U1ItTMWr5emdGjE" 
# consumer_secret = "DMcdKA9hAP5il1blT2sKZMowBYG5uiKvOxihZKeB7Xw2uzQQLk" 
# access_token = "801246156340740096-eNUEV9IyTsPE0aPuwGpG52S9gVjAzzI"
# access_token_secret = "sdq7i2lqRCAEiEYyoX32enxgGtUgJZLmkr02et541YbkF"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)

###fixing multi-key mistake
# mdf = pd.read_csv(r'main_datasets\mirror_tw_mentionedby_08122021_full.csv', index_col=0)
# mdf_2 = pd.read_csv(r'main_datasets\mirror_tw_mentionedby_08122021_full_2.csv', index_col=0)

# mdf = pd.concat([mdf,mdf_2],axis=1)
# mdf = mdf.loc[:,~mdf.columns.duplicated()]
# mdf.to_csv(r'main_datasets\mirror_tw_mentionedby_08122021_full.csv')

#mentions by a user
mdf = pd.read_csv(r'main_datasets\mirror_tw_mentionedby_08122021_full.csv', index_col=0)
mentioned_by = mdf.to_dict(orient="list")

# users_left = list(set(users)-set(mdf.columns)) #it's possible that many of these are private/skipped_users
# pd.Series(users_left)[:int(len(list(users_left))/2)].to_csv(r'main_datasets\mirror_tw_mentionedby_users1.csv')
# pd.Series(users_left)[int(len(list(users_left))/2)-1:].to_csv(r'main_datasets\mirror_tw_mentionedby_users2.csv')

users_left_1 = pd.read_csv(r'main_datasets\mirror_tw_mentionedby_users1.csv', index_col=0)
users_left_2 = pd.read_csv(r'main_datasets\mirror_tw_mentionedby_users2.csv', index_col=0)

# mentioned_by = {}
for user in tqdm(users_left_1["0"]):
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
        mdf.to_csv(r'main_datasets\mirror_tw_mentionedby_08122021_full.csv')

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