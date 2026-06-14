import os
import json

# Define paths
TEAMS_CONFIG_PATH = os.path.join("data", "worldcup_teams.json")
OUTPUT_PATH = os.path.join("data", "sticker_database.json")

def clean_club_name(club_name):
    """Cleans the club name for file paths (replaces non-alphanumeric with underscores)."""
    if not club_name:
        return "no_club"
    cleaned = "".join([c if c.isalnum() else "_" for c in club_name])
    return cleaned

def update_database():
    if not os.path.exists(TEAMS_CONFIG_PATH):
        print(f"Error: {TEAMS_CONFIG_PATH} not found!")
        return
        
    # 1. Die aktuelle Database laden statt neu zu schreiben
    if not os.path.exists(OUTPUT_PATH):
        print(f"Error: Existing database {OUTPUT_PATH} not found. Bitte zuerst initial generieren.")
        return

    with open(TEAMS_CONFIG_PATH, "r", encoding="utf-8") as f:
        teams_config = json.load(f)
        
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        sticker_database = json.load(f)
        
    teams_data = teams_config.get("teams", {})
    groups = teams_config.get("groups", {})

    print("Aktualisiere die bestehende Panini Sticker Database...")

    # 2. Alle Sondersticker werden ignoriert. Wir iterieren nur durch die Teams für die Spieler-Infos.
    for group_letter, group_teams in groups.items():
        for team_key in group_teams:
            team_info = teams_data.get(team_key)
            if not team_info:
                print(f"Warning: Team {team_key} not defined in configuration.")
                continue

            code = team_info.get("country_code")  # e.g., "ECU"
            folder = team_info.get("folder")
            country_json_path = os.path.join("data", folder, "info.json")

            if not os.path.exists(country_json_path):
                print(f"File not found: {country_json_path}. Skipping players for {code}.")
                continue

            with open(country_json_path, "r", encoding="utf-8") as cf:
                country_data = json.load(cf)

            # 3. Neue Attribute aus der info.json extrahieren (Fallback auf leeren String, falls nicht vorhanden)
            color_1 = country_data.get("color_1", "")
            color_2 = country_data.get("color_2", "")
            color_3 = country_data.get("color_3", "")
            
            # Pfad für die Flagge generieren
            flag_path = f"./data/{folder}/{team_key}_flag.png"

            players_list = country_data.get("players", [])
            
            # Die 26 Spielerslots durchlaufen und in der Database updaten
            for j in range(26):
                p_num = str(j + 3).zfill(3)
                player_sticker_id = f"{code}{p_num}"
                
                # Prüfen, ob der Sticker in der bestehenden Database existiert
                if player_sticker_id in sticker_database:
                    sticker = sticker_database[player_sticker_id]
                    
                    # Nur bei Einträgen vom Typ player oder placeholder aktiv werden
                    if sticker.get("type") in ["player", "player_placeholder"]:
                        # Die neuen Felder hinzufügen
                        sticker["color_1"] = color_1
                        sticker["color_2"] = color_2
                        sticker["color_3"] = color_3
                        sticker["flag"] = flag_path
                        
                        # Aktualisiert gleichzeitig bestehende Spielerdaten aus der info.json
                        if j < len(players_list):
                            player = players_list[j]
                            
                            sticker["type"] = "player"
                            sticker["first_name"] = player.get("first_name")
                            sticker["last_name"] = player.get("last_name")
                            sticker["jersey_number"] = player.get("jersey_number")
                            sticker["position"] = player.get("position", "ST")
                            
                            pos = sticker["position"]
                            pos_class = "pos-at"
                            if pos == "GK": 
                                pos_class = "pos-gk"
                            elif pos in ["LB", "CB", "RB"]: 
                                pos_class = "pos-df"
                            elif pos in ["DM", "CM", "AM"]: 
                                pos_class = "pos-mf"
                            
                            sticker["posClass"] = pos_class
                            sticker["birthdate"] = player.get("birthdate", "—")
                            sticker["height"] = player.get("height", "—")
                            sticker["club_name"] = player.get("club", "No Club")
                            sticker["club_image"] = f"./data/{folder}/clubs/{clean_club_name(player.get('club'))}.png"
                            sticker["image"] = f"./data/{folder}/players/{player.get('jersey_number')}.png"

    # Speichern der bearbeiteten Database
    with open(OUTPUT_PATH, "w", encoding="utf-8") as out_f:
        json.dump(sticker_database, out_f, indent=2, ensure_ascii=False)

    print("\n=====================================================")
    print(f"ERFOLG! Database wurde aktualisiert: {OUTPUT_PATH}")
    print("=====================================================\n")

if __name__ == "__main__":
    update_database()