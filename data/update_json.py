import json

filename = 'sticker_database.json'

# JSON-Datei einlesen
with open(filename, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Alle Einträge durchsuchen
for key, item in data.items():
    if item.get("type") == "team_photo":
        team_key = item.get("teamKey", "")
        
        # Neues Dictionary aufbauen, um die Reihenfolge der Zeilen zu erhalten
        new_item = {}
        for k, v in item.items():
            new_item[k] = v
            # Sobald "image" geschrieben wurde, "flag" direkt darunter einfügen
            if k == "image":
                new_item["flag"] = f"./data/{team_key}/{team_key}_flag_circle.png"
        
        # Den alten Eintrag mit dem neuen überschreiben
        data[key] = new_item

# Geänderte Daten wieder in die Datei schreiben
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Die Datei wurde erfolgreich aktualisiert!")