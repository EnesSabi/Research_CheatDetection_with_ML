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

# Emre 19.05. 
exe ist erstellt, Json files werden im dist Ordner gespeichert (Ka ob problematisch oder ob es besser geht)
exe wurde mit pyinstaller erstellt mit pyinstaller --noconsole --onefile program_live.py
cx freeze kommt nicht auf manche bibliotheken klar und pyinstaller spackt manchmal rum bei Dateipfaden

    # TODO:
    json datei wird angelegt, auch wenn kein game gefunden wurde. Also bei next_game_filename eine Blockade einfügen,
    dass er bei nicht gefunden games keine json Datei erstellt oder noch besser: Nur eine Json Datei erstellt, wenn 
    ein snapshot gemacht wurde

