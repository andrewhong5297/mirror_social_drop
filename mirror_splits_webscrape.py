# -*- coding: utf-8 -*-
"""
Created on Sun Jul 18 20:51:44 2021

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

cols = ["creator","split_address","etherscan_address","total_recieved","ENS_publication"] 
data = pd.DataFrame(columns=cols, index=np.arange(1000))
# myurl = "https://mirror.xyz/splits/"
myurl = "https://etherscan.io/exportData?type=address&a="

sp = pd.read_csv(r'main_datasets\mirror_supplied\Splits.csv')
split_addresses = list(set(sp["contract_address"]))

# etherscan_api_key = "FQKZCMUAQUA688R7FVDIH9BGD6698JIFPZ"

# address = split_addresses[0]

df_idx=0
for address in split_addresses:
    driver.get(myurl+address)
    
    time.sleep(5)
    
    soup = BeautifulSoup(
        driver.page_source, "html.parser"
    )


    df_idx+=1

#may need to explore etherscan api