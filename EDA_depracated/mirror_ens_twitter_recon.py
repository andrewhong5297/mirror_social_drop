# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 10:41:03 2021

@author: Andrew
"""
import pandas as pd
import numpy as np
import datetime

import requests
from bs4 import BeautifulSoup

from tqdm import tqdm
import time 

df = pd.read_csv(r'C:/Users/Andrew/OneDrive - nyu.edu/Documents/Python Script Backup/datasets/mirror_leaders_wens.csv', index_col=0)
ens_addresses = pd.read_csv(r'C:\Users\Andrew\OneDrive - nyu.edu\Documents\Python Script Backup\datasets\dune_scrapes\mirror_ens_addresses.csv')

untwittered_ens = set(ens_addresses["ENS"]) - set(df["ENS"].apply(lambda x: "https://{}".format(x)))
twitters_without_ens = set(df[df["ENS"]=="no ens"]["Username"])

ens_address = dict(zip(ens_addresses["ENS"],ens_addresses["Address"]))
        
def attach_address(x):
    try:
        return ens_address[x]
    except:
        pass

df["Address"] = df["ENS"].apply(lambda x: attach_address("https://{}".format(x)))        
df.to_csv(r'C:/Users/Andrew/OneDrive - nyu.edu/Documents/Python Script Backup/datasets/mirror_leaders_waddresses.csv')

### legacy
# ens_twitter = dict()
# for ens in df["ENS"].unique():
#     print(ens)
#     if ens=="no ens":
#         pass
#     else:
#         req = requests.get("https://{}".format(ens))
#         soup = BeautifulSoup(
#             req.text, "xml"
#         )  # could use 'lxml or html.parser too, see https://stackoverflow.com/questions/45494505/python-difference-between-lxml-and-html-parser-and-html5lib-with-beautifu?rq=1
#         try:
#             holder = soup.find('div',{'class':'css-c6ixvj'})
#             ens_address[ens]=holder.find('a')['href'].split('/')[-1]
#         except:
#             print("nothing published yet")

###we need dune data for
#all crowdfunds
#all editions
#all reserve auctions
#all splits
#all NFT minted articles
