# IMPORTS
from riotwatcher import LolWatcher, ApiError, RiotWatcher
from dotenv import load_dotenv

import json
import pandas as pd
import time
import os

# VARIABLES

load_dotenv()

api_key = os.getenv("RIOT_API_KEY")
region = os.getenv("REGION")
platform = os.getenv("PLATFORM")

lol_watcher = LolWatcher(api_key)
riot_watcher = RiotWatcher(api_key)

all_matches = {}
match_data = []
summoner_list = []
results = []
accounts = []
match_id_list = []

# PARAMETER
summoners_txt = 'summoners_euw.txt'
all_matches_json = '../JSONS/all_matches.json'
participants_json = 'participants.json'
puuid_json = 'puuid_accounts.json'


def read_summoner_list():
    with open(summoners_txt, 'r') as file:
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
        account = riot_watcher.account.by_riot_id(platform, split_summoner_list[summoners][0], split_summoner_list[summoners][1])
        accounts.append(account)
        match_ids = lol_watcher.match.matchlist_by_puuid(platform, account['puuid'], count=1)
        match_id_list.append(match_ids)

    print(accounts)

def summoner_to_json():
    for account, match_ids in zip(accounts, match_id_list):
        match_data = []

        for match_id in match_ids:
            match = lol_watcher.match.by_id(platform, match_id)
            match_data.append(match)
            time.sleep(1.5)

        all_matches[account['gameName']] = match_data
        print(f"Retrieved {len(match_data)} matches for {account['gameName']}\n")

    print(all_matches)

    with open(all_matches_json, 'w') as file:
        json.dump(all_matches, file, indent=2)

    all_participants = []

    for summoner, matches in all_matches.items():
        if matches:
            participants = matches[0]['metadata']['participants']
            all_participants.extend(participants)

    # Delete duplicates
    all_participants = list(set(all_participants))

    with open(participants_json, 'w') as file:
        json.dump(all_participants, file, indent=2)

def rank_tier_extraction():
    with open(all_matches_json, "r") as file:
        all_matches = json.load(file)

    for match_list in all_matches.values():
        for match in match_list:
            for participant in match["info"]["participants"]:
                puu_id = participant.get("puuid")

                if puu_id:
                    try:
                        summoner_data = lol_watcher.summoner.by_puuid("euw1", puu_id)
                        summoner_id = summoner_data["id"]

                        rank_entries = lol_watcher.league.by_summoner("euw1", summoner_id)
                        solo_rank = next((entry for entry in rank_entries if entry["queueType"] == "RANKED_SOLO_5x5"), None)

                        if solo_rank:
                            participant["tier"] = solo_rank["tier"]
                            participant["rank"] = solo_rank["rank"]
                            participant["leaguePoints"] = solo_rank["leaguePoints"]
                            participant["hotStreak"] = solo_rank["hotStreak"]
                            participant["veteran"] = solo_rank["veteran"]
                            participant["freshBlood"] = solo_rank["freshBlood"]
                            participant["wins"] = solo_rank["wins"]
                            participant["losses"] = solo_rank["losses"]
                        else:
                            participant["tier"] = "UNRANKED"
                            participant["rank"] = None
                            participant["leaguePoints"] = 0

                        time.sleep(0.5)

                    except Exception as e:
                        print(f"Fehler bei {participant.get('summonerName', '??')}: {e}")
                        participant["tier"] = "ERROR"
                        participant["rank"] = None
                        participant["leaguePoints"] = None

    with open(all_matches_json, "w") as file:
        json.dump(all_matches, file, indent=2)

def fetching_more_accounts():
    with open(participants_json, 'r') as file:
        summoner_idx = json.load(file)

    summoner_idx = sorted(set(p for p in summoner_idx if isinstance(p, str) and len(p) > 20))

    for idx, puuid in enumerate(summoner_idx, 1): #enumerate is just für a counter for us to know how many summoners we have
        try:
            account = riot_watcher.account.by_puuid(platform, puuid)
            results.append({
                "ID": idx,
                "gameName": account.get("gameName"),
                "tagLine": account.get("tagLine"),
                "puuid": puuid
            })
            time.sleep(1.2)  # Respect Riot API rate limits
        except Exception as e:
            results.append({
                "ID": idx,
                "error": str(e),
                "puuid": puuid
            })

    with open(puuid_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # TODO: Find out what these "weird" values mean in some entries in puuid_accounts.json and sort them out if necessary --> These are non latin letters like ü or korean. We can just work with them.

def test():
    with open(summoners_txt, 'r') as file:
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

    print(split_summoner_list)
    return

if __name__ == "__main__":
    read_summoner_list()
    summoner_to_json()
    rank_tier_extraction()
    fetching_more_accounts()