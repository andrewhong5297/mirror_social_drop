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

df = pd.read_csv(r'C:/Users/Andrew/OneDrive - nyu.edu/Documents/Python Script Backup/datasets/mirror_leaders.csv', index_col=0)

# ens = df["ENS"].unique()[0]

ens_address = dict()
for ens in df["ENS"].unique():
    print(ens)
    if ens=="no ens":
        pass
    else:
        req = requests.get("https://{}".format(ens))
        soup = BeautifulSoup(
            req.text, "xml"
        )  # could use 'lxml or html.parser too, see https://stackoverflow.com/questions/45494505/python-difference-between-lxml-and-html-parser-and-html5lib-with-beautifu?rq=1
        try:
            holder = soup.find('div',{'class':'css-c6ixvj'})
            ens_address[ens]=holder.find('a')['href'].split('/')[-1]
        except:
            print("nothing published yet")
        
def attach_address(x):
    try:
        return ens_address[x]
    except:
        pass

df["address"] = df["ENS"].apply(lambda x: attach_address(x))        
df.to_csv(r'C:/Users/Andrew/OneDrive - nyu.edu/Documents/Python Script Backup/datasets/mirror_leaders_waddresses.csv')

###we need dune data for
#all crowdfunds
#all editions
#all nft auctions
#all splits
