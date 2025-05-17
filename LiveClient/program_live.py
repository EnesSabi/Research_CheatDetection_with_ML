# IMPORTS
import datetime
import getpass
import glob
import json
import os
import threading
import time
import tkinter as tk
from tkinter import scrolledtext

import requests
import ttkbootstrap as tb
import urllib3

# WARNINGS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# VARIABLES
username = getpass.getuser()
running = False


# FUNCTIONS
def get_next_game_filename(userid):
    files = glob.glob(f"extract_{userid}_game*.json")
    game_number = len(files) + 1
    return f"extract_{userid}_game{game_number}.json"


FILENAME = get_next_game_filename(username)

if not os.path.exists(FILENAME):
    with open(FILENAME, "w") as f:
        json.dump([], f)


def tracking_loop(log_widget, status_label):
    while True:
        try:
            response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
        except requests.exceptions.ConnectionError:
            msg = f"{datetime.datetime.now()} | Currently not in game"
            status_label.config(text="🕹️ Nicht im Spiel", bootstyle="warning")
            log_widget.insert(tk.END, msg + "\n")
            log_widget.see(tk.END)
            time.sleep(5)
            if not running:
                break
            continue
        if response.status_code != 404:
            try:
                data = response.json()
                game_time = data["gameData"]["gameTime"]
                new_data = {
                    "timestamp": game_time,
                    "data": data
                }

                with open(FILENAME, "r") as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                    existing_data.append(new_data)

                with open(FILENAME, "w") as f:
                    json.dump(existing_data, f, indent=2)

                msg = f"{datetime.datetime.now()} | ✅ Snapshot gespeichert"
                status_label.config(text="✅ Spiel erkannt", bootstyle="success")
            except Exception as e:
                msg = f"{datetime.datetime.now()} | ❌ Fehler: {e}"
                status_label.config(text="❌ Fehler", bootstyle="danger")
        else:
            msg = f"{datetime.datetime.now()} | Kein Spiel gefunden"
            status_label.config(text="🔍 Kein Match", bootstyle="info")

        log_widget.insert(tk.END, msg + "\n")
        log_widget.see(tk.END)
        time.sleep(5)


def start_tracking(log_widget, status_label):
    global running
    if not running:
        running = True
        threading.Thread(target=tracking_loop, args=(log_widget, status_label), daemon=True).start()
        status_label.config(text="⏳ Läuft...", bootstyle="info")


def stop_tracking(status_label):
    global running
    running = False
    status_label.config(text="⛔ Gestoppt", bootstyle="secondary")


def build_gui():
    root = tb.Window(themename="darkly")
    root.title("Live Game Tracker")
    root.geometry("700x450")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    # Überschrift
    tb.Label(root, text="🎮 LoL Live Tracker", font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))

    status_label = tb.Label(root, text="Status: Inaktiv", font=("Segoe UI", 12), bootstyle="secondary")
    status_label.pack(pady=5)

    # Button-Leiste
    button_frame = tb.Frame(root)
    button_frame.pack(pady=5)

    tb.Button(button_frame, text="Start", bootstyle="success-outline", width=20,
              command=lambda: start_tracking(log_area, status_label)).grid(row=0, column=0, padx=10)

    tb.Button(button_frame, text="Stop", bootstyle="danger-outline", width=20,
              command=lambda: stop_tracking(status_label)).grid(row=0, column=1, padx=10)

    # Log-Bereich
    log_area = scrolledtext.ScrolledText(root, width=85, height=17, font=("Consolas", 10), bg="#1e1e1e", fg="#eeeeee",
                                         insertbackground="#ffffff")
    log_area.pack(padx=10, pady=10)

    root.mainloop()


build_gui()
