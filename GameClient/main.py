# IMPORTS

from riotwatcher import LolWatcher, ApiError, RiotWatcher
from dotenv import load_dotenv

import json
import pandas as pd
import time
import os

# DATA AND VARIABLES

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")
region = os.getenv("REGION")
platform = os.getenv("PLATFORM")

lol_watcher = LolWatcher(api_key)
riot_watcher = RiotWatcher(api_key)

all_matches = {}
match_data = []
summoner_list = []

# FETCH DATA OF SUMMONERS

with open('summoners_euw.txt', 'r') as file:
    summoner_names = file.readlines()

for names in summoner_names:
    user_name = names.strip("#")
    summoner_list.append(user_name)

split_summoner_list = []
for item in summoner_list:
    if '#' in item:
        parts = item.split('#')
        split_parts = [part.strip() for part in parts]
        split_summoner_list.append(split_parts)
    else:
        split_summoner_list.append([item.strip()])

for summoners in range(len(split_summoner_list)):
    account = riot_watcher.account.by_riot_id(platform, split_summoner_list[summoners][0], split_summoner_list[summoners][1])                        # TODO: gameName muss parametrisiert werden für Liste als Feed
    match_ids = lol_watcher.match.matchlist_by_puuid(platform, account['puuid'], count=1)

# TODO: SummonerName ist parametrisiert, aber der nachfolgende code wird mit dem letzten Eintrag ausgeführt (evtl. alles in die for-schleife einschieben)

for match_id in match_ids:
    match = lol_watcher.match.by_id(platform, match_id)
    match_data.append(match)
    time.sleep(1.5)

all_matches[account['gameName']] = match_data
print(f"Retrieved {len(match_data)} matches for {account['gameName']}\n")

print(all_matches)

with open('../JSONS/all_matches.json', 'w') as file:
    json.dump(all_matches, file, indent=2)

with open('participants.json', 'w') as file:
    json.dump(all_matches['Agurin'][0]["metadata"]["participants"][1:], file, indent=2)                     # TODO: gameName muss parametrisiert werden



'''
for name in summoner_names:
    try:
        print(f" Processing {name}")

        account = riot_watcher.account.by_riot_id(region, name, 'sudo')
        
        

        match_ids = lol_watcher.match.matchlist_by_puuid(platform, puuid, count=5)
        match_data = []

        for match_id in match_ids:
            match = lol_watcher.match.by_id(platform, match_id)
            match_data.append(match)
            time.sleep(1.5)

        all_matches[name] = match_data
        
        print(f"Retrieved {len(match_data)} matches for {name}\n")

    except ApiError as e:
        print(f"Error processing {name}: {e}\n")

# Optional: Matches speichern
with open("all_matches.json", "w") as f:
    json.dump(all_matches, f, indent=2)
'''
