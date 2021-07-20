# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 13:03:00 2021

@author: Andrew
"""

import pandas as pd

"""

start recon to get missing contracts/creations from contributions

"""

all_missing_contracts = {}

##dune is showing 17 crowdfunds, here we see 27. 
cf = pd.read_csv(r'main_datasets\mirror_supplied\Crowdfunds.csv')
cf["creator"] = cf["creator"].apply(lambda x: x.lower())
cf["contract_address"] = cf["contract_address"].apply(lambda x: x.lower())

cf_cont = pd.read_csv(r'main_datasets\dune_data\mirror_cf_all_graph.csv')
missing_creator = {'\\x41ed7d49292b8fbf9b9311c1cb4d6eb877646c58':'0x48A63097E1Ac123b1f5A8bbfFafA4afa8192FaB0', 
                   '\\xa338f6960d1e8bcde50a8057173229dcaa4428c9':'0xA0Cf798816D4b9b9866b5330EEa46a18382f251e',
                   '\\x94515e4f6fabad73c8bcdd8cd42f0b5c037e2c49': '0xc3268ddb8e38302763ffdc9191fcebd4c948fe1b'}

def fill_missing(x):
    try:
        return missing_creator[x]
    except:
        return x

cf_cont["creator"] = cf_cont["contract_address"].apply(lambda x: fill_missing(x)) 
cf_cont[["contributor","contract_address","creator"]]=cf_cont[["contributor","contract_address","creator"]].applymap(lambda x: x.replace("\\","0"))

remaining_cf = set(cf["contract_address"]) - set(cf_cont["contract_address"])

all_missing_contracts["crowdfunds"] = list(remaining_cf)

##dune is showing just editions from one contract, here there are 5 with two of them being crowdfund editions 
##56 total created with 37 having been purchased from. This seems right 
ed = pd.read_csv(r'main_datasets\mirror_supplied\Editions.csv')
ed["creator"] = ed["creator"].apply(lambda x: x.lower())

ed_cont = pd.read_csv(r'main_datasets\dune_data\mirror_ed_all_graph.csv') #could join with timestamp too in future, would need more accurate timestamp from mirror supplied data
ed_cont[["buyer","contract_address","fundingRecipient"]]=ed_cont[["buyer","contract_address","fundingRecipient"]].applymap(lambda x: x.replace("\\","0"))
ed[["contract_address","creator","fundingRecipient"]] = ed[["contract_address","creator","fundingRecipient"]].applymap(lambda x: x.lower())
ed = ed.drop_duplicates(subset=["contract_address","creator","fundingRecipient","edition_name"])
ed_merged = pd.merge(ed_cont,ed, how="left", on=["contract_address","org_quantity","fundingRecipient","org_price"])

remaining_ed = set(ed[["contract_address","creator","edition_name"]].apply(tuple, axis=1)) - set(ed_merged[["contract_address","creator","edition_name"]].apply(tuple, axis=1))

all_missing_contracts["editions (contract, creator, edition_name"] = list(remaining_ed)

# ##dune doesn't have all auctions yet, here we see 49
# au = pd.read_csv(r'main_datasets\mirror_supplied\ReserveAuctions.csv')
# au["creator"] = au["creator"].apply(lambda x: x.lower())
# created_au = au.pivot_table(index="creator",values="token_id",aggfunc=lambda x: len(x.unique()))
# created_au = dict(zip(created_au.index,created_au.token_id))

##splits were covered by supplied data, in the future will require more of a dune setup. 

mc = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in all_missing_contracts.items() ]))
#SAVE AS CSV AS YOU GO
mc.to_csv(r'main_datasets\missing_contracts.csv')
