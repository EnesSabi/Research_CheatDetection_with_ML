# IMPORTS
from riotwatcher import LolWatcher, ApiError, RiotWatcher
from dotenv import load_dotenv
import json
import time
import os
from tqdm import tqdm  # Progress bars
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

# ----------- NEU: Generic Retry-Wrapper für alle API-Requests -----------
def riot_api_request(func, *args, max_retries=3, **kwargs):
    for attempt in range(1, max_retries+1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[Retry {attempt}/{max_retries}] Fehler: {e}")
            if attempt == max_retries:
                raise

def read_summoner_list(summoners_txt: str) -> List[List[str]]:
    """Reads summoner names from file and returns a list of [gameName, tagLine]."""
    summoner_list = []
    with open(summoners_txt, 'r', encoding = 'utf-8') as file:
        for line in file:
            name = line.strip().strip("#")
            if '#' in name:
                parts = [part.strip() for part in name.split('#')]
                summoner_list.append(parts)
            else:
                summoner_list.append([name])
    return summoner_list

def fetch_accounts_and_matchids(summoner_infos: List[List[str]]) -> (List[Dict[str, Any]], List[List[str]]):
    accounts = []
    match_id_list = []

    for info in tqdm(summoner_infos, desc='Fetching accounts & match IDs'):
        try:
            # Does playername and tag exist?
            if len(info) < 2:
                print(f"Überspringe fehlerhaften Eintrag (falsches Format): {info}")
                continue

            # get Account Data
            account = riot_api_request(
                riot_watcher.account.by_riot_id,
                platform,
                info[0],
                info[1]
            )                                               # 1000 Req every Minute

            # If Account is empty --> skip
            if not account or "puuid" not in account:
                print(f"Keine Daten gefunden für: {info}")
                continue

            # get Match-IDs
            match_ids = riot_api_request(
                lol_watcher.match.matchlist_by_puuid,
                platform,
                account['puuid'],
                count=1
            )                                               # 2000 Req/10 Sec

            accounts.append(account)
            match_id_list.append(match_ids)

        except ApiError as e:
            # 404 = player not found
            if e.response.status_code == 404:
                print(f"Spieler nicht gefunden (404): {info}")
                continue
            else:
                raise
        except Exception as e:
            print(f"Fehler bei {info}: {e}")
            continue

    return accounts, match_id_list

def fetch_and_save_matches(accounts: List[Dict[str, Any]], match_id_list: List[List[str]], out_json: str):
    """Fetches match data for all accounts and saves to json files."""
    all_matches = {}

    for account, match_ids in tqdm(zip(accounts, match_id_list), desc='Fetching match data', total=len(accounts)):
        match_data = []
        for match_id in match_ids: # potenziell Langwierig
            match = riot_api_request(lol_watcher.match.by_id, platform, match_id) # 2000 Req/10 Sec
            match_data.append(match)
            # time.sleep(1.2)  # Respect Riot API rate limits
        all_matches[account['gameName']] = match_data
        # print(f"Retrieved {len(match_data)} matches for {account['gameName']}")  # Entfernt, ersetzt durch Ladebalken

    # Save matches and participants
    with open(out_json, 'w') as file:
        json.dump(all_matches, file, indent=2)

def enrich_participant_ranks(matches_json: str):
    """Enriches each participant in all matches with solo queue rank info."""
    with open(matches_json, "r") as file:
        all_matches = json.load(file)

    for match_list in tqdm(all_matches.values(), desc='Enriching matches', position=0):
        for match in match_list:
            for participant in match["info"]["participants"]: #tqdm( __, desc='Participant Ranks', leave=False, position=1)
                puu_id = participant.get("puuid")
                if not puu_id:
                    continue
                try:
                    summoner_data = riot_api_request(lol_watcher.summoner.by_puuid, "euw1", puu_id) # 1600 requests per Minute
                    time.sleep(0.1)
                    summoner_id = summoner_data["id"]
                    rank_entries = riot_api_request(lol_watcher.league.by_summoner, "euw1", summoner_id) # 100 requests per Minute
                    time.sleep(0.9)
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
                    #time.sleep(0.5)
                except Exception as e:
                    print(f"Fehler bei {participant.get('summonerName', '??')}: {e}")
                    participant.update({
                        "tier": "ERROR",
                        "rank": None,
                        "leaguePoints": None
                    })

    with open(matches_json, "w") as file:
        json.dump(all_matches, file, indent=2)

def test_summoner_list(summoners_txt: str):
    with open(summoners_txt, 'r') as file:
        summoner_names = file.readlines()

    split_summoner_list = []
    for name in summoner_names:
        name = name.strip().strip("#")
        if '#' in name:
            parts = [part.strip() for part in name.split('#')]
            split_summoner_list.append(parts)
        else:
            split_summoner_list.append([name])
    print(split_summoner_list)
    return

if __name__ == "__main__":
    summoner_infos = read_summoner_list(summoners_txt)
    accounts, match_id_list = fetch_accounts_and_matchids(summoner_infos) # 8:10 Min mit 2.34s/it - Pause bei 50er --> 1000 Req/Min Grenze
    fetch_and_save_matches(accounts, match_id_list, all_matches_json) # 4:09 Min mit 1.19s/it - Pause bei 80er --> 1000 Req/Min Grenze
    enrich_participant_ranks(all_matches_json) # 1:24:47 mit 1.84it/s --> 30 sekunden Run mit 1Min30Sec
    #12:19
    #1:37:06
    #2:15:35