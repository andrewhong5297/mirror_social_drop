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

myurl = "https://duneanalytics.com/queries/80679"
driver.get(myurl)

time.sleep(3)
    
soup = BeautifulSoup(
    driver.page_source, "html.parser"
)

pages = len(soup.find('select', {'aria-label':'Select page'}).find_all('option'))

# addresses = []

column = ["buyer","valuebought","seller"]

data = pd.DataFrame(columns=column, index=np.arange(pages*25))

df_idx=0
for page in range(pages):
    soup = BeautifulSoup(
        driver.page_source, "html.parser"
    )
    rows = soup.find_all('tr', {'role':'row'})
    for row in rows[1:]:
        cells = row.find_all('td', {'role':'cell'})
        data["buyer"][df_idx] = cells[0].text.replace('\\','0')
        data["valuebought"][df_idx] = cells[1].text
        data["seller"][df_idx] = cells[2].text.replace('\\','0')
        df_idx+=1
    driver.find_element_by_xpath('//*[@id="tabs--33--panel--0"]/div/div/ul/li[6]/button').click()

driver.quit()

data.to_csv(r'main_datasets\dune_data\mirror_ed_graph.csv')