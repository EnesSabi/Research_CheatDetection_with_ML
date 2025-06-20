# IMPORTS
from riotwatcher import LolWatcher, ApiError, RiotWatcher
from dotenv import load_dotenv
import json
import pandas as pd
import time
import os
from typing import List, Dict, Any

# Load environment variables
load_dotenv()
api_key = os.getenv("RIOT_API_KEY")
region = os.getenv("REGION")
platform = os.getenv("PLATFORM")

# RiotWatcher Setup
lol_watcher = LolWatcher(api_key)
riot_watcher = RiotWatcher(api_key)

# File paths
summoners_txt = 'summoners_euw.txt'
all_matches_json = '../JSONS/all_matches.json'
participants_json = '../JSONS/participants.json'
puuid_json = '../JSONS/puuid_accounts.json'

# ----------- NEU: Generic Retry-Wrapper für alle API-Requests -----------
def riot_api_request(func, *args, max_retries=3, sleep=2, **kwargs):
    for attempt in range(1, max_retries+1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[Retry {attempt}/{max_retries}] Fehler: {e}")
            if attempt == max_retries:
                raise
            time.sleep(sleep * attempt)  # Exponentiell steigende Pause

def read_summoner_list(summoners_txt: str) -> List[List[str]]:
    """Reads summoner names from file and returns a list of [gameName, tagLine]."""
    summoner_list = []
    with open(summoners_txt, 'r') as file:
        for line in file:
            name = line.strip().strip("#")
            if '#' in name:
                parts = [part.strip() for part in name.split('#')]
                summoner_list.append(parts)
            else:
                summoner_list.append([name])
    return summoner_list

def fetch_accounts_and_matchids(summoner_infos: List[List[str]]) -> (List[Dict[str, Any]], List[List[str]]):
    """Fetches account info and recent match ids for each summoner."""
    accounts = []
    match_id_list = []
    for info in summoner_infos:
        account = riot_api_request(riot_watcher.account.by_riot_id, platform, info[0], info[1])
        accounts.append(account)
        match_ids = riot_api_request(lol_watcher.match.matchlist_by_puuid, platform, account['puuid'], count=1)
        match_id_list.append(match_ids)
    return accounts, match_id_list

def fetch_and_save_matches(accounts: List[Dict[str, Any]], match_id_list: List[List[str]], out_json: str, participants_json: str):
    """Fetches match data for all accounts and saves to json files."""
    all_matches = {}
    all_participants = set()

    for account, match_ids in zip(accounts, match_id_list):
        match_data = []
        for match_id in match_ids:
            match = riot_api_request(lol_watcher.match.by_id, platform, match_id)
            match_data.append(match)
            time.sleep(1.5)  # Respect Riot API rate limits
        all_matches[account['gameName']] = match_data
        print(f"Retrieved {len(match_data)} matches for {account['gameName']}")

        # Participants extraction
        if match_data:
            participants = match_data[0]['metadata']['participants']
            all_participants.update(participants)

    # Save matches and participants
    with open(out_json, 'w') as file:
        json.dump(all_matches, file, indent=2)
    with open(participants_json, 'w') as file:
        json.dump(list(all_participants), file, indent=2)

def enrich_participant_ranks(matches_json: str):
    """Enriches each participant in all matches with solo queue rank info."""
    with open(matches_json, "r") as file:
        all_matches = json.load(file)

    for match_list in all_matches.values():
        for match in match_list:
            for participant in match["info"]["participants"]:
                puu_id = participant.get("puuid")
                if not puu_id:
                    continue
                try:
                    summoner_data = riot_api_request(lol_watcher.summoner.by_puuid, "euw1", puu_id)
                    summoner_id = summoner_data["id"]
                    rank_entries = riot_api_request(lol_watcher.league.by_summoner, "euw1", summoner_id)
                    solo_rank = next((entry for entry in rank_entries if entry["queueType"] == "RANKED_SOLO_5x5"), None)
                    if solo_rank:
                        participant.update({
                            "tier": solo_rank["tier"],
                            "rank": solo_rank["rank"],
                            "leaguePoints": solo_rank["leaguePoints"],
                            "hotStreak": solo_rank["hotStreak"],
                            "veteran": solo_rank["veteran"],
                            "freshBlood": solo_rank["freshBlood"],
                            "wins": solo_rank["wins"],
                            "losses": solo_rank["losses"]
                        })
                    else:
                        participant.update({
                            "tier": "UNRANKED",
                            "rank": None,
                            "leaguePoints": 0
                        })
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Fehler bei {participant.get('summonerName', '??')}: {e}")
                    participant.update({
                        "tier": "ERROR",
                        "rank": None,
                        "leaguePoints": None
                    })

    with open(matches_json, "w") as file:
        json.dump(all_matches, file, indent=2)

def fetch_account_data_for_participants(participants_json_path: str, output_json_path: str):
    """Fetches account info for participants and saves as JSON."""
    with open(participants_json_path, 'r') as file:
        puuid_list = json.load(file)

    puuid_list = sorted(set(p for p in puuid_list if isinstance(p, str) and len(p) > 20))
    results = []

    for idx, puuid in enumerate(puuid_list, 1):
        try:
            account = riot_api_request(riot_watcher.account.by_puuid, platform, puuid)
            results.append({
                "ID": idx,
                "gameName": account.get("gameName"),
                "tagLine": account.get("tagLine"),
                "puuid": puuid
            })
            time.sleep(1.2)
        except Exception as e:
            results.append({
                "ID": idx,
                "error": str(e),
                "puuid": puuid
            })

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

def test_summoner_list(summoners_txt: str):
    """Test helper to show how summoner names are split."""
    with open(summoners_txt, 'r') as file:
        summoner_names = file.readlines()

    split_summoner_list = []
    for name in summoner_names:
        name = name.strip().strip("#")
        if '#' in name:
            parts = [part.strip() for part in name.split('#')]
            split_summoner_list.append(parts)
        else:
            split_summoner_list.append([nme])
    print(split_summoner_list)
    return

if __name__ == "__main__":
    # 1. Read summoner list
    summoner_infos = read_summoner_list(summoners_txt)
    # 2. Fetch account and match IDs
    accounts, match_id_list = fetch_accounts_and_matchids(summoner_infos)
    # 3. Fetch and save match and participant data
    fetch_and_save_matches(accounts, match_id_list, all_matches_json, participants_json)
    # 4. Enrich with ranks
    enrich_participant_ranks(all_matches_json)
    # 5. Fetch account data for all participants
    fetch_account_data_for_participants(participants_json, puuid_json)