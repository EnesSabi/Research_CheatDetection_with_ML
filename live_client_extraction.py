import os
import requests
import time
import datetime
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if not os.path.exists("extract.json"):
    with open("extract.json", "w") as f:
        json.dump([], f)

while True:
    try:
        response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
    except requests.exceptions.ConnectionError:
        # Try again every 5 seconds
        print('{} | Currently not in game'.format(datetime.datetime.now()))
        time.sleep(5)
        continue

    if response.status_code != 404:
        try:
            data = response.json()
            gameTime = data["gameData"]["gameTime"]
            new_data = {
                "timestamp": gameTime,  # datetime.datetime.now().isoformat(),
                "data": data}

            with open("extract.json", "r") as f:
                existing_data = json.load(f)
                existing_data.append(new_data)

            with open("extract.json", "w") as f:
                json.dump(existing_data, f, indent=2)
            print(f'{datetime.datetime.now()} | Snapshot gespeichert')
        except requests.exceptions.ConnectionError as e:
            print(e)
    time.sleep(5)

