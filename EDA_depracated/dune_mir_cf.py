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

from web3 import Web3

num_jobs = np.arange(1080,step=10)

driver = webdriver.Chrome()

myurl = "https://duneanalytics.com/queries/83918"
driver.get(myurl)

time.sleep(3)
    
soup = BeautifulSoup(
    driver.page_source, "html.parser"
)

pages = len(soup.find('select', {'aria-label':'Select page'}).find_all('option'))

# addresses = []

column = ["contributor","contribution","creator","contract_address"]

data = pd.DataFrame(columns=column, index=np.arange(pages*25))

missing_creator = {'\\x41ed7d49292b8fbf9b9311c1cb4d6eb877646c58':'0x48A63097E1Ac123b1f5A8bbfFafA4afa8192FaB0', 
                   '\\xa338f6960d1e8bcde50a8057173229dcaa4428c9':'0xA0Cf798816D4b9b9866b5330EEa46a18382f251e',
                   '\\x94515e4f6fabad73c8bcdd8cd42f0b5c037e2c49': '0xc3268ddb8e38302763ffdc9191fcebd4c948fe1b'}

df_idx=0
for page in range(pages):
    soup = BeautifulSoup(
        driver.page_source, "html.parser"
    )
    rows = soup.find_all('tr', {'role':'row'})
    for row in rows[1:]:
        cells = row.find_all('td', {'role':'cell'})
        data["contributor"][df_idx] = cells[0].text.replace('\\','0')
        data["contribution"][df_idx] = cells[1].text
        try:
            data["contract_address"][df_idx] = cells[2].text.replace('\\','0')
            data["creator"][df_idx] = missing_creator[cells[2].text]
        except:
            data["creator"][df_idx] = cells[3].text.replace('\\','0')
        df_idx+=1
    driver.find_element_by_xpath('//*[@id="tabs--33--panel--0"]/div/div/ul/li[6]/button').click()

driver.quit()

data.dropna(how="all", inplace=True)
data.to_csv(r'main_datasets\dune_data\mirror_cf_contonly.csv')

"""data cleaning"""
### one time creator + ENS mapping after scrape cf
df = pd.read_csv(r'main_datasets\dune_data\mirror_cf_contonly.csv', index_col=0)
# ens = pd.read_csv(r'main_datasets\dune_data\mirror_ens_addresses.csv', index_col=0)

# address_ens = dict(zip(ens["Address"],ens["ENS"]))
# address_ens["0x48A63097E1Ac123b1f5A8bbfFafA4afa8192FaB0"] = 'https://scott.mirror.xyz'
# address_ens["0x48a63097e1ac123b1f5a8bbffafa4afa8192fab0"] = 'https://scott.mirror.xyz'
# address_ens["0xc3268ddb8e38302763ffdc9191fcebd4c948fe1b"] = 'https://creators.mirror.xyz' #seems to be duplicate account?
# def convert_ens(x):
#     try:
#         return address_ens[x]
#     except:
#         print(x)
#         pass #not a registered writer, probably dev account

# df["ENS"] = df["creator"].apply(lambda x: convert_ens(x))

# df.dropna(how="any",inplace=True)
# df.to_csv(r'main_datasets\dune_data\mirror_cf_contonly.csv')

#crowdfund scrape for fund cap requires the mirror ENS + crowdfund address, so {ENS} + "/{}".format(crowdfundaddress)
