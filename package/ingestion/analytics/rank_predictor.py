RANK_THRESHOLDS = {
    "Rookie": {"IV": 0, "III": 250, "II": 500, "I": 750},
    "Bronze": {"IV": 1000, "III": 1500, "II": 2000, "I": 2500},
    "Silver": {"IV": 3000, "III": 3500, "II": 4000, "I": 4500},
    "Gold": {"IV": 5250, "III": 6000, "II": 6750, "I": 7500},
    "Platinum": {"IV": 8250, "III": 9000, "II": 10000, "I": 11000},
    "Diamond": {"IV": 12000, "III": 13000, "II": 14000, "I": 15000},
    "Masters": {"I": 16000},
}

ENTRY_COSTS = {
    "Rookie": 0,
    "Bronze": 10,
    "Silver": 20,
    "Gold": 38,
    "Platinum": 48,
    "Diamond": 65,
    "Masters": 90,
}

def predict_games(current_rp, session_rp_gross, session_games, current_rank_name, target_rank, target_div):
    if session_games <= 0:
        print("Games played must be greater than 0.")
        return None

    # Normalize input to handle casing issues
    target_rank = target_rank.strip()
    target_div = target_div.strip().upper()

    # Handle Masters having no division
    if target_rank.lower() in ["master", "masters"]:
        target_rank = "Masters"
        target_div = "I"

    entry_cost = ENTRY_COSTS.get(current_rank_name, 0)

    net_session_rp = session_rp_gross - (entry_cost * session_games)
    avg_net_rp_per_game = net_session_rp / session_games

    target_rp = RANK_THRESHOLDS.get(target_rank, {}).get(target_div)

    if target_rp is None:
        print(f"Invalid rank or division entered. Got: '{target_rank}' '{target_div}'")
        return None

    if current_rp >= target_rp:
        print("You are already at or above that rank.")
        return None

    if avg_net_rp_per_game <= 0:
        print("\nWarning: Your current average RP per game is less than the entry cost.")
        print(f"You are losing {abs(avg_net_rp_per_game)} RP per game on average.")
        print("At this rate you will not reach your target rank.")
        return None
    
    rp_needed = target_rp - current_rp
    games_needed = rp_needed / avg_net_rp_per_game

    return {
        "entry_cost_per_game": entry_cost,
        "avg_gross_rp_per_game": round(session_rp_gross / session_games, 1),
        "avg_net_rp_per_game": round(avg_net_rp_per_game, 1),
        "rp_needed": rp_needed,
        "games_needed": round(games_needed)
    }