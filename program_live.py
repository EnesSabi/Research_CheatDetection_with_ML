import os
import json
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from riotwatcher import LolWatcher, ApiError, RiotWatcher

# .env laden
load_dotenv()
api_key = os.getenv("RIOT_API_KEY")
region = os.getenv("REGION", "euw1")

watcher = LolWatcher(api_key)
riot_watcher = RiotWatcher(api_key=api_key)


def check_live_game():
    summoner_name = entry.get()
    if not summoner_name:
        messagebox.showwarning("Fehler", "Bitte gib einen Summoner-Namen ein.")
        return
    summoner_name_split = summoner_name.split('#')
    try:
        summoner = riot_watcher.account.by_riot_id(region, summoner_name_split[0], summoner_name_split[1])
        game = watcher.spectator.by_summoner(region, summoner['id'])

        output = f"{summoner_name} ist gerade im Spiel!\nModus: {game['gameMode']}\n\nSpieler im Match:"
        for p in game['participants']:
            output += f"\n - {p['summonerName']} (Champion ID: {p['championId']})"

        # Optional speichern
        with open("current_game.json", "w", encoding="utf-8") as f:
            json.dump(game, f, indent=2)

        result_label.config(text=output)

    except ApiError as e:
        if e.response.status_code == 404:
            result_label.config(text=f"{summoner_name} ist derzeit nicht im Spiel.")
        else:
            messagebox.showerror("API Fehler", f"Ein Fehler ist aufgetreten: {e}")
    except Exception as ex:
        messagebox.showerror("Fehler", str(ex))



# === GUI Setup ===
root = tk.Tk()
root.title("LoL Live Game Checker")

tk.Label(root, text="Summoner Name:").pack(pady=5)
entry = tk.Entry(root, width=30)
entry.pack(pady=5)

tk.Button(root, text="Suche starten", command=check_live_game).pack(pady=10)

result_label = tk.Label(root, text="", justify="left", wraplength=400)
result_label.pack(padx=10, pady=10)

root.mainloop()
