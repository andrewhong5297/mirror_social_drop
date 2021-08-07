# -*- coding: utf-8 -*-
"""
Created on Thu Jun 17 08:22:48 2021

@author: Andrew
"""

import pandas as pd
import numpy as np
import datetime

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from tqdm import tqdm
import time 

driver = webdriver.Chrome()

myurl = "https://mirror.xyz/race"
driver.get(myurl)

time.sleep(10)

#select leaderboards
driver.find_element_by_css_selector("#__next > div > div:nth-child(2) > div > div > div.css-1tfpx04 > div:nth-child(2) > div.css-z60yai > div.css-1ntr13f > button.css-1ve6lcz").click()

i=0
while i<2: 
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    i+=1

#expand all
details = driver.find_elements_by_class_name('css-dcbupf') 
for x in range(0,len(details)):
    try:
        details[x].click()
    except:
        pass

cols = ["Username","Round"] 
data = pd.DataFrame(columns=cols, index=np.arange(10000))

soup = BeautifulSoup(
    driver.page_source, "html.parser"
)

# rounds = soup.find_all("div", {"class":"WaitlistList css-qaq7os"})

winners = soup.find_all('div',{'class':'css-1onmluk'})
winners_text = [winner.text for winner in winners]

# df_idx=0
# for idx, a_round in enumerate(rounds):
#     winners = a_round.find_all('li')
#     print(idx)
#     #need to segment round_winner and voters... also need to decide if the data represents the "vote_to" or the "username"
#     if idx == len(rounds)-1:
#         for winner in winners:
#             print(winner.find('div',{'class':'css-1onmluk'}).text)
#             data["Username"][df_idx] = winner.find('div',{'class':'css-1onmluk'}).text
#             data["Round"][df_idx] = 0 
#             df_idx+=1
#     else:
#         for winner in winners:
#             # try:
#             print(winner.find('div',{'class':'css-1onmluk'}).text)
#             data["Username"][df_idx] = winner.find('div',{'class':'css-1onmluk'}).text
#             data["Round"][df_idx] = len(rounds)-idx-2
#             df_idx+=1
#             # except:
#                 # pass
                
# driver.quit()

print("current number of writers: {}".format(len(data["Username"].unique())))
data.dropna(how="all",inplace=True)
data.to_csv(r'main_datasets/mirror_leaders.csv')

# voter = all_voters[0]
# winner=winners[0]
# a_round=rounds[0]    

### in case of overwrite, genesis is here
# stateful.mirror.xyz
# g.mirror.xyz
# jk.mirror.xyz
# joonian.mirror.xyz
# helloshreyas.mirror.xyz
# linda.mirror.xyz
# d.mirror.xyz
# darkstar.mirror.xyz
# no ens
# ls.mirror.xyz
# jake.mirror.xyz
# j.mirror.xyz
# coopahtroopa.mirror.xyz
# danny.mirror.xyz
# jammsession.mirror.xyz
# variant.mirror.xyz
# no ens

