# mirror_social_drop
 
https://www.notion.so/Mirror-Data-Analysis-and-WRITE-Airdrop-Proposal-cd5cc3be4e1c45d1be1cf95ada4d1804#afbe4035a225487a966cd2ed23e613b6

repo structure:

- all dune py files help get data for editions, crowdfunds, auctions, and splits (saved in main_datasets -> dune_data). There are some extra manualy reconcilliations that are made for these WIP
- for running order, it's mirror_graph_network.py (formatting all graph data to get centrality measurements) then mirror_all_features_recon.py (for rewards calculations/visualizations).

still left to do:
- [ ]  get all reserve auction version data (v2, v3, and v4 still being decoded for dune. May then map it back to the NFTfactory for sanity checks)
- [ ]  get all tiered crowdfunds (still being decoded for dune)
- [ ]  reconcile why some splits aren't appearing in dune (https://duneanalytics.com/queries/84423), only 21 splits show up, and 7 in the old splits. Missing at least 20 somewhere
- [ ]  editions don't have a creator, instead event logs just show the funds receipient who I have labelled as the creator. This may be undesireable 
- [ ]  crowdfunds don't have caps in event logs, this will have to be scraped manually later (not for airdrop but for our_network)
- [ ]  clean twitter mentions data (currently taking the mentions from their most recent 2000 tweets, may need to go for 5000). 
- [ ]  some visualizations on how voting influence has shifted, maybe make editions NFT from this
- [ ]  check that QA creators and contributions are removed from data
- [ ]  check that those without Twitter handles don't get the `hasVoted` bool rewards
- [ ]  check that those who aren't part of the extra rewards are still part of the airdrop (i.e. those I removed who voted for themselves, or haven't voted at all)
- [ ]  try to implement PageRank of splits? could be an extra weighted multiplier on creator rewards, rather than the number of splits created. Could take percentages into account too.