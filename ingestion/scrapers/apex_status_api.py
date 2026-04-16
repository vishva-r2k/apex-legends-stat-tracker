import requests
from ingestion.analytics.rank_predictor import predict_games

import os
API_KEY = os.environ.get("APEX_API_KEY")

def fetch_player_stats(player_name):
    url = "https://api.mozambiquehe.re/bridge?auth=YOUR_API_KEY&player=PLAYER_NAME&platform=PLATFORM"

    params = {
        "auth": API_KEY,
        "player": player_name,
        "platform": "PC"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Error:", response.status_code)
        print(response.text)
        return None

    return response.json()

def parse_player_stats(data):
    global_stats = data.get("global", {})
    total_stats = data.get("total", {})
    
    result = {
        "name": global_stats.get("name"),
        "platform": global_stats.get("platform"),
        "level": global_stats.get("level"),
        "kills": total_stats.get("kills", {}).get("value"),
        "damage": total_stats.get("specialEvent_damage", {}).get("value"),
    }

    return result

def parse_legend_stats(data):
    legends_data = data.get("legends", {}).get("all", {})
    legends = []

    for legend_name, legend_info in legends_data.items():
        if legend_name == "Global":
            continue
        stats = legend_info.get("data", [])

        if not stats:
            continue  # skip legends with no tracked stats

        legend_stats = {
            "legend": legend_name,
            "kills": None,
            "damage": None
        }

        for stat in stats:
            stat_key = stat.get("key")
            if stat_key == "kills":
                legend_stats["kills"] = stat.get("value")
            elif stat_key == "specialEvent_damage":
                legend_stats["damage"] = stat.get("value")

        legends.append(legend_stats)

    return legends

def parse_rank_info(data):
    rank_data = data.get("global", {}).get("rank", {})
    
    return {
        "rankName": rank_data.get("rankName"),
        "rankDiv": rank_data.get("rankDiv"),
        "rankScore": rank_data.get("rankScore")
    }

from ingestion.processors.save_data import save_to_file

if __name__ == "__main__":
    player_name = input("Enter player name: ")
    data = fetch_player_stats(player_name)

    if not data:
        print("No data returned.")
        exit()

    player = parse_player_stats(data)
    legends = parse_legend_stats(data)
    rank = parse_rank_info(data)

    print(f"Player: {player['name']} | Platform: {player['platform']} | Level: {player['level']}")
    print(f"\nCurrent Rank: {rank['rankName']} {rank['rankDiv']}")
    print(f"Current RP: {rank['rankScore']}")

    session_rp = int(input("\nHow much RP did you gain this session? "))
    session_games = int(input("How many games did you play this session? "))
    target_rank = input("What rank do you want to reach? (Silver/Gold/Platinum/Diamond/Masters): ")

    if target_rank.lower() in ["master", "masters"]:
        target_rank = "Masters"
        target_div = "I"
    else:
        target_div = input("What division? (IV/III/II/I): ")

    prediction = predict_games(rank["rankScore"], session_rp, session_games, rank["rankName"], target_rank, target_div)
    
    if prediction:
        print(f"\nEntry cost per game: {prediction['entry_cost_per_game']} RP")
        print(f"Average gross RP per game: {prediction['avg_gross_rp_per_game']}")
        print(f"Average net RP per game (after entry cost): {prediction['avg_net_rp_per_game']}")
        print(f"RP needed: {prediction['rp_needed']}")
        print(f"At your current rate, you'll hit {target_rank} {target_div} in {prediction['games_needed']} games.")

    output = {
        "player": player,
        "legends": legends,
        "rank": rank,
        "prediction": prediction
    }

    save_to_file(output)