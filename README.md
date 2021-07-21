# mirror_social_drop
 
https://www.notion.so/Mirror-Data-Analysis-and-WRITE-Airdrop-Proposal-cd5cc3be4e1c45d1be1cf95ada4d1804#afbe4035a225487a966cd2ed23e613b6

repo structure:

- all dune py files help get data for editions, crowdfunds, auctions, and splits (saved in main_datasets -> dune_data). There are some extra manualy reconcilliations that are made for these WIP
- for running order, run scripts 1_, 2_, and 3_ for graph networks. 

for updating data in the future:

- require updates from mirror team for all created splits, auctions, crowdfunds, and editions
- require dune updates for contributors across auctions, crowdfunds, and editions. splits needs to be manual due to missing data (possible missing contract to be decoded)
- require udpates from mirror team for twitter-ethereum address verification and votes.json file
- require an update to twitter mentions data

still left to do:
- [ ]  make sure all contracts missing in missing_contracts.csv really had no one purchase or contribute to them (so far editions and crowdfunds are included)
- [x]  clean twitter mentions data (currently taking the mentions from their most recent 2000 tweets, may need to go for 5000). 
- [ ]  check that QA creators and contributions are removed from data. Can probably do this if I have the addresses used for testing.
- [ ]  remove all contributions from creator or contract to splits, editions, crowdfunds, and auctions.
- [x]  editions don't have a creator, instead event logs just show the funds receipient who I have labelled as the creator. This may be undesireable 
- [x]  check that those without Twitter handles don't get the `hasVoted` bool rewards
- [x]  check that those who aren't part of the extra rewards are still part of the airdrop (i.e. those I removed who voted for themselves, or haven't voted at all)
- [x]  expand on writing of article intro in notion
- [x]  expand on formula derivation thought process, tying it to changes in the intro

dune tasks
- [x]  make contributors graph queries for auctions
- [x]  get all reserve auction version data (v2, v3, and v4 still being decoded for dune. May then map it back to the NFTfactory for sanity checks)
- [x]  get all tiered crowdfunds (still being decoded for dune)

formula/algo improvements
- [ ]  try to implement PageRank of splits? could be an extra weighted multiplier on creator rewards, rather than the number of splits created. Could take percentages into account too.
- [x]  add splits and auctions and twitter data to the graph

later when article after proposal: 
- [ ]  some visualizations on how voting influence has shifted, maybe make editions NFT from this
- [ ]  crowdfunds don't have caps in event logs, this will have to be scraped manually later (not for airdrop but for our_network)
- [ ]  do some KPIs in dune dashboard