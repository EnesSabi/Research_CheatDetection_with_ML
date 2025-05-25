# Enes 17.04
Ich habe erstmal alles übertragen auf das ipynb → damit es besser aussieht, erstmal ipynb weiter machen

# Enes 15.05
Ich werde mich morgen daran setzen, dass wir auch Live-Daten fetchen können.
Dazu könnte man wahrscheinlich die Live-API verwenden.
Als weiteren Schritt werde ich eine MongoDB oder MySQL Datenbank errichten und nutzen.

Vanguard bietet leider keine Interaktionsmöglichkeiten.
Keine Datasets über bekannte Cheater.

# Emre 16.05. 
Live_Client API fertig umgesetzt, 
moderne GUI erstellt,
requirements.txt angelegt,
exe Datei angelegt (funktioniert noch nicht, da die Bibliotheken nicht mitgenommen werden) --> siehe dist\live_client_extraction.exe

# Emre 18.05.
program_live.py debugging (Stopp Knopf hat nicht funktioniert wenn man In-Game ist)
Übearbeiten von jupyter notebook datei program_live
Versuchen eine exe zu erstellen mit CX Freeze (anstatt PyInstaller) --> Funktioniert immernoch nicht [setup.py ist für CX Freeze damit er ein build machen kann]

# Enes 19.05
- Fokus auf Machine Learning detectable
- Visible Cheats should be the first task
- Improve Precision and minimize False Positives
- Do Client-Side heuristics for the Events
- Main Focus on Scripting Vectors and the predictions of Auto Cancel, Kites and Evade Scripts
- Start the Work with the Live-Data and then implement the Rest.
- Asap v1.0 to distribute and update later with other features.

# Emre 19.05. 
exe ist erstellt, Json files werden im dist Ordner gespeichert (Ka ob problematisch oder ob es besser geht)
exe wurde mit pyinstaller erstellt mit pyinstaller --noconsole --onefile program_live.py
cx freeze kommt nicht auf manche bibliotheken klar und pyinstaller spackt manchmal rum bei Dateipfaden

    # TODO:
    json datei wird angelegt, auch wenn kein game gefunden wurde. Also bei next_game_filename eine Blockade einfügen,
    dass er bei nicht gefunden games keine json Datei erstellt oder noch besser: Nur eine Json Datei erstellt, wenn 
    ein snapshot gemacht wurde

# Emre 23.05.
live game daten werden derzeit gesammelt. 
Readme file wurde ergänzt mit infos über LiveClient
13 Volle Summoners Rift games eingefügt (Json files) --> manche waren auch mit ff (generell: 0,5 MB pro Spielminute)
Ersten dataframe erstellt, sortiert nach Gametime und Game --> Gametime == timestamp leider, also nicht wirklich eine "Sekunde 0" möglich
Beim Dataframe Probleme: - glob findet nur bis game9, da single digit integer
                         - summonerName gibt KeyError
Dataframe Probleme wurden gelöst --> Da die snapshots bereits im Ladescreen starten, viele NaN Values

# Emre 25.05. 
Weiter am Dataframe gearbeitet.
    - Score-Daten von allPlayers eingefügt (davor nur Infos über activePlayer im DF)
    - Erste Filter angewandet, damit Ladescreen snapshots ausgefiltert werden

    # TODO: 
    -Es wurden bewusst NaN Datenpunkte eingefügt, da über andere Player keine active-Daten (gold etc.)vorhanden sind 
        --> Problem: Was ist wenn da noch natürliche NaN Daten sind, also nicht bewusste?
    -Bei allPlayers wird eine Liste erstellt namens items. Diese items haben auch ein price was dort steht
        --> Schätzen wie viel Gold ein Spieler hat (durch Minions, kills, bounty, assist, wards, naturliche goldgenerierung)
        --> Oder einfach zählen was seine Items kosten --> Das ist sein Gold (einfacher, aber ungenau)

# Enes 25.05.
1. Mathematische Formel für Goldproduktion des aktiven Spielers (siehe Vorschlag Emre 25.05. --> Schätzung), Vergleich zu Item-prices
2. Json files names über matchid speichern, und effizienteres Json-Abfragen (nicht mehrmals das gleiche extrahieren --> z.B. Runen)
3. Feature Selection Vorbereitung --> welche Daten sind wichtig? 

Conclusion --> Focus on catching cheaters after the game (must not be live) --> Allows Usage of GameClient stats
