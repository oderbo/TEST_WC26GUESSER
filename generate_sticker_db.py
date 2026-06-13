import os
import json

# Define paths
TEAMS_CONFIG_PATH = os.path.join("data", "worldcup_teams.json")
OUTPUT_PATH = os.path.join("data", "sticker_database.json")

# Configuration for manual special stickers
TOTAL_STADIUMS = 16  # 16 stadiums total * 2 halves = 32 slots
TOTAL_GOLDEN_BOOT = 28
TOTAL_GOLDEN_BALL = 22
TOTAL_WINNERS = 22

sticker_database = {}
current_album_number = 0  # Sequential numbering for the album slots

def clean_club_name(club_name):
    """Cleans the club name for file paths (replaces non-alphanumeric with underscores)."""
    if not club_name:
        return "no_club"
    cleaned = "".join([c if c.isalnum() else "_" for c in club_name])
    return cleaned

def generate_database():
    global current_album_number
    
    if not os.path.exists(TEAMS_CONFIG_PATH):
        print(f"Error: {TEAMS_CONFIG_PATH} not found!")
        return

    with open(TEAMS_CONFIG_PATH, "r", encoding="utf-8") as f:
        teams_config = json.load(f)
        
    teams_data = teams_config.get("teams", {})
    groups = teams_config.get("groups", {})

    print("Starting generation of Panini sticker database...")

    # =========================================================================
    # 1. PAGE 1: INTRO (Sticker 00 + 6 Specials)
    # =========================================================================
    
    # The 00 Stamp
    sticker_database["SPC000"] = {
        "id": "SPC000",
        "albumNumber": "00",
        "type": "special",
        "name": "FIFA World Cup 2026 Stamp",
        "image": "./assets/specials/special_00.png",
        "shiny": "gold",
        "orientation": "portrait"
    }

    # The 6 further specials (SPC001 to SPC006)
    special_names = [
        "WC Trophy (Top)",
        "WC Trophy (Bottom)",
        "Oli in Gold",
        "Official Match Ball",
        "Tournament Logo",
        "FIFA Shiny Gold"
    ]

    for i in range(1, 7):
        current_album_number += 1
        id_str = f"SPC{str(i).zfill(3)}"
        
        part_value = None
        if i == 1: part_value = "top"
        elif i == 2: part_value = "bottom"

        sticker_database[id_str] = {
            "id": id_str,
            "albumNumber": str(current_album_number),
            "type": "special",
            "name": special_names[i - 1],
            "image": f"./assets/specials/{id_str.lower()}.png",
            "shiny": "gold",
            "orientation": "landscape" if i <= 2 else "portrait"
        }
        if part_value:
            sticker_database[id_str]["part"] = part_value

    # =========================================================================
    # 2. STADIUMS (STD001 - STD032) -> Changed to 16 Stadiums (32 Slots)
    # =========================================================================
    stadium_count = 1
    for i in range(1, TOTAL_STADIUMS + 1):
        id_pad = str(i).zfill(2)
        
        # Left half
        current_album_number += 1
        id_left = f"STD{str(stadium_count).zfill(3)}"
        sticker_database[id_left] = {
            "id": id_left,
            "albumNumber": str(current_album_number),
            "type": "stadium",
            "name": f"Stadium {id_pad} - Left Half",
            "image": f"./assets/stadiums/stadium_{id_pad}_left.png",
            "shiny": "none",
            "orientation": "portrait",
            "part": "left"
        }
        stadium_count += 1

        # Right half
        current_album_number += 1
        id_right = f"STD{str(stadium_count).zfill(3)}"
        sticker_database[id_right] = {
            "id": id_right,
            "albumNumber": str(current_album_number),
            "type": "stadium",
            "name": f"Stadium {id_pad} - Right Half",
            "image": f"./assets/stadiums/stadium_{id_pad}_right.png",
            "shiny": "none",
            "orientation": "portrait",
            "part": "right"
        }
        stadium_count += 1

    def process_group_block(group_letters):
        global current_album_number
        for group_letter in group_letters:
            group_teams = groups.get(group_letter, [])
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

                # --- 1. TEAM PHOTO (Code + "001") -> First sticker slot for a nation
                current_album_number += 1
                team_photo_id = f"{code}001"
                sticker_database[team_photo_id] = {
                    "id": team_photo_id,
                    "albumNumber": str(current_album_number),
                    "type": "team_photo",
                    "name": f"{country_data.get('teamName')} Team Photo",
                    "image": f"./data/{folder}/team_photo.png",
                    "shiny": "none",
                    "orientation": "landscape",
                    "teamKey": team_key,
                    "countryCode": code
                }

                # --- 2. LOGO / BADGE (Code + "002") -> Second sticker slot, Shiny Silver
                current_album_number += 1
                badge_id = f"{code}002"
                sticker_database[badge_id] = {
                    "id": badge_id,
                    "albumNumber": str(current_album_number),
                    "type": "logo",  # Changed type to 'logo'
                    "name": f"{country_data.get('teamName')} Logo",  # Changed name format
                    "image": f"./data/{folder}/logo.png",
                    "shiny": "silver",
                    "orientation": "portrait",
                    "teamKey": team_key,
                    "countryCode": code
                }

                # --- 3. PLAYERS (Code + "003" to "028")
                players_list = country_data.get("players", [])
                for j in range(26):  # Fills exactly 26 player spots
                    current_album_number += 1
                    p_num = str(j + 3).zfill(3)
                    player_sticker_id = f"{code}{p_num}"

                    if j < len(players_list):
                        player = players_list[j]
                        
                        # --- DATA INTEGRITY CHECK & WARNINGS ---
                        missing_fields = []
                        if not player.get("position"): missing_fields.append("position")
                        if not player.get("birthdate"): missing_fields.append("birthdate")
                        if not player.get("height"): missing_fields.append("height")
                        if not player.get("club"): missing_fields.append("club")
                        
                        if missing_fields:
                            p_name = f"{player.get('first_name', '')} {player.get('last_name', 'Unknown')}".strip()
                            print(f"-> WARNING: Player '{p_name}' ({code}) is missing fields: {', '.join(missing_fields)}")
                        # ---------------------------------------

                        pos = player.get("position", "ST")
                        
                        # Exact position mapping to posClass requested
                        pos_class = "pos-at" # Default fallback
                        if pos == "GK": 
                            pos_class = "pos-gk"
                        elif pos in ["LB", "CB", "RB"]: 
                            pos_class = "pos-df"
                        elif pos in ["DM", "CM", "AM"]: 
                            pos_class = "pos-mf"
                        elif pos in ["LW", "ST", "RW"]: 
                            pos_class = "pos-at"

                        sticker_database[player_sticker_id] = {
                            "id": player_sticker_id,
                            "albumNumber": str(current_album_number),
                            "type": "player",
                            "first_name": player.get("first_name"),
                            "last_name": player.get("last_name"),
                            "jersey_number": player.get("jersey_number"),
                            "position": pos,
                            "posClass": pos_class,
                            "birthdate": player.get("birthdate", "—"),  # Included birthdate
                            "height": player.get("height", "—"),
                            "club_name": player.get("club", "No Club"),
                            "club_image": f"./data/{folder}/clubs/{clean_club_name(player.get('club'))}.png",
                            "image": f"./data/{folder}/players/{player.get('jersey_number')}.png",
                            "teamName": country_data.get("teamName"),
                            "teamKey": team_key,
                            "countryCode": code,
                            "shiny": "none",
                            "orientation": "portrait"
                        }
                    else:
                        # Placeholder in case JSON has fewer than 26 players
                        sticker_database[player_sticker_id] = {
                            "id": player_sticker_id,
                            "albumNumber": str(current_album_number),
                            "type": "player_placeholder",
                            "name": f"Player Spot {j + 3}",
                            "teamName": country_data.get("teamName"),
                            "countryCode": code,
                            "shiny": "none",
                            "orientation": "portrait"
                        }

    # =========================================================================
    # 3. TEAMS GROUPS A-D (16 Teams)
    # =========================================================================
    process_group_block(["A", "B", "C", "D"])

    # =========================================================================
    # 4. GOLDEN BOOT (GBO001 - GBO028) -> Shiny Silver
    # =========================================================================
    for i in range(1, TOTAL_GOLDEN_BOOT + 1):
        current_album_number += 1
        id_str = f"GBO{str(i).zfill(3)}"
        sticker_database[id_str] = {
            "id": id_str,
            "albumNumber": str(current_album_number),
            "type": "golden_boot",
            "name": f"Golden Boot Winner {i}",
            "image": f"./assets/awards/boot_{i}.png",
            "shiny": "silver",
            "orientation": "portrait"
        }

    # =========================================================================
    # 5. TEAMS GROUPS E-H (16 Teams) -> Includes Ecuador
    # =========================================================================
    process_group_block(["E", "F", "G", "H"])

    # =========================================================================
    # 6. GOLDEN BALL (GBA001 - GBA022) -> Shiny Gold
    # =========================================================================
    for i in range(1, TOTAL_GOLDEN_BALL + 1):
        current_album_number += 1
        id_str = f"GBA{str(i).zfill(3)}"
        sticker_database[id_str] = {
            "id": id_str,
            "albumNumber": str(current_album_number),
            "type": "golden_ball",
            "name": f"Golden Ball Winner {i}",
            "image": f"./assets/awards/ball_{i}.png",
            "shiny": "gold",
            "orientation": "portrait"
        }

    # =========================================================================
    # 7. TEAMS GROUPS I-L (16 Teams)
    # =========================================================================
    process_group_block(["I", "J", "K", "L"])

    # =========================================================================
    # 8. HISTORIC WINNER TEAMS (WIN001 - WIN022) -> Shiny Gold, Landscape
    # =========================================================================
    for i in range(1, TOTAL_WINNERS + 1):
        current_album_number += 1
        id_str = f"WIN{str(i).zfill(3)}"
        sticker_database[id_str] = {
            "id": id_str,
            "albumNumber": str(current_album_number),
            "type": "historic_winner",
            "name": f"Historic World Cup Winner {i}",
            "image": f"./assets/historic/winner_{i}.png",
            "shiny": "gold",
            "orientation": "landscape"
        }

    # Write to final sticker database JSON file
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as out_f:
        json.dump(sticker_database, out_f, indent=2, ensure_ascii=False)

    print("\n=====================================================")
    print(f"SUCCESS! Database created at: {OUTPUT_PATH}")
    print(f"Final consecutive album index number: {current_album_number}")
    print(f"Total registered sticker entries: {len(sticker_database)}")
    print("=====================================================\n")

if __name__ == "__main__":
    generate_database()