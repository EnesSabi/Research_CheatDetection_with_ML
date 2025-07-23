from bs4 import BeautifulSoup
import glob
import os

# Only for DeepNote
path = os.path.join(os.path.dirname(__file__), "NameScrapeTxt")

#Find all files with .txt
files = sorted(glob.glob(os.path.join(path, "*.txt")))

players = []

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    rows = soup.select("tr")

    for row in rows:
        name = row.select_one("span.whitespace-pre-wrap.text-gray-900")
        tag = row.select_one("span.text-gray-500.truncate")

        if name and tag:
            player_name = name.text.strip()
            player_tag = tag.text.strip()
            players.append(f"{player_name}{player_tag}")

#Drop Duplicates
players = list(set(players))

print(players)
print(f"{len(players)} Spieler gefunden")

with open("alle_spieler.txt", "w", encoding="utf-8") as f:
    for p in players:
        f.write(p + "\n")
