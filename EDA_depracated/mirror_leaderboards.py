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

# i=0
# while i<4: 
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     time.sleep(3)
#     i+=1

#expand all
details = driver.find_elements_by_class_name('css-dcbupf') 
for x in range(0,len(details)):
    try:
        details[x].click()
    except:
        pass

#max I've seen is 400, so div 10 is 40. Still have to go through and manually click sometimes, page is weird.
expand = 0
while expand < 50:
    print(expand)
    inner_details = driver.find_elements_by_class_name('css-17nut0g') 
    for x in range(0,len(inner_details)):
        try:
            inner_details[x].click()
        except:
            pass
    expand+=1

#start scraping, reuse old? how to reconcile and update? maybe rescrape last two rounds?
df = pd.read_csv(r'C:/Users/Andrew/OneDrive - nyu.edu/Documents/Python Script Backup/datasets/mirror_leaders_wens.csv', index_col=0)

cols = ["Username","Round","Vote_From","Vote_Amount","Round_Winner","Total_Votes","ENS","Address"] 
data = pd.DataFrame(columns=cols, index=np.arange(10000))

soup = BeautifulSoup(
    driver.page_source, "html.parser"
)

rounds = soup.find_all("div", {"class":"WaitlistList css-qaq7os"})

df_idx=0
for idx, a_round in enumerate(rounds):
    winners = a_round.find_all('li')
    
    #need to segment round_winner and voters... also need to decide if the data represents the "vote_to" or the "username"
    if idx == len(rounds)-1:
        for winner in winners:
            data["Username"][df_idx] = winner.find('div',{'class':'css-1onmluk'}).text
            data["Round_Winner"][df_idx] = True
            data["Round"][df_idx] = 0 
            #add ENS manually
            data["Total_Votes"][df_idx] = 0
            data["Vote_From"][df_idx] = "genesis"
            data["Vote_Amount"][df_idx] = 0
            df_idx+=1
    else:
        for winner in winners:
            all_voters = winner.find_all('div', {'class':'css-1r0ztxp'})
            for voter in all_voters:    
                data["Username"][df_idx] = winner.find('div',{'class':'css-1onmluk'}).text
                data["Round_Winner"][df_idx] = True
                data["Round"][df_idx] = len(rounds)-idx-1
                #check for ENS created
                possible_ens = winner.find('div',{'class':'css-1sjhlb0'}).text
                data["ENS"][df_idx] =  possible_ens if "mirror.xyz" in possible_ens else "no ens"
                #address is left blank for now
                data["Total_Votes"][df_idx] = winner.find('button',{'class':'css-fdij71'}).text.split(" ")[0].replace(",","")
                data["Vote_From"][df_idx] = "@" + voter.find('a')['href'].split('/')[-1]
                data["Vote_Amount"][df_idx] = voter.find('div', {'class':'css-13dzaxp'}).text
                df_idx+=1

driver.quit()

print("current number of writers: {}".format(len(data["Username"].unique())))
data.dropna(how="all",inplace=True)
data.to_csv(r'C:\Users\Andrew\OneDrive - nyu.edu\Documents\Python Script Backup\datasets\mirror_leaders.csv')
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

