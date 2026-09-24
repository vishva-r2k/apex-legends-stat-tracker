# MMR Estimator
# NOTE: Apex Legends MMR is hidden and not exposed by the API.
# This is an estimation based on session performance compared to
# expected averages for each rank tier. It is not guaranteed to
# reflect your actual MMR.

RANK_ORDER = [
    "Rookie",
    "Bronze",
    "Silver",
    "Gold",
    "Platinum",
    "Diamond",
    "Masters"
]

# Expected average NET rp per game (after entry cost) for each rank tier
# Based on community data and rank distribution research
EXPECTED_AVG_NET_RP = {
    "Rookie": 15,
    "Bronze": 18,
    "Silver": 22,
    "Gold": 26,
    "Platinum": 30,
    "Diamond": 36,
    "Masters": 45
}

ENTRY_COSTS = {
    "Rookie": 0,
    "Bronze": 10,
    "Silver": 20,
    "Gold": 38,
    "Platinum": 48,
    "Diamond": 65,
    "Masters": 90
}

def estimate_mmr_gap(current_rank_name, session_rp_gross, session_games):
    """
    Estimates the gap between a player's visible rank and their likely MMR tier.
    
    Args:
        current_rank_name: The player's current visible rank (e.g. "Platinum")
        session_rp_gross: Total raw RP gained this session before entry costs
        session_games: Number of games played this session
    
    Returns:
        A dictionary containing the estimation results
    """

    if session_games <= 0:
        print("Games played must be greater than 0.")
        return None

    if current_rank_name not in RANK_ORDER:
        print(f"Invalid rank: {current_rank_name}")
        return None

    # Calculate net RP per game after entry costs
    entry_cost = ENTRY_COSTS.get(current_rank_name, 0)
    net_session_rp = session_rp_gross - (entry_cost * session_games)
    avg_net_rp_per_game = net_session_rp / session_games

    # Get the expected average for the player's current rank
    expected_avg = EXPECTED_AVG_NET_RP.get(current_rank_name, 0)

    # Calculate the difference between actual and expected performance
    performance_diff = avg_net_rp_per_game - expected_avg

    # Estimate MMR tier based on performance difference
    current_rank_index = RANK_ORDER.index(current_rank_name)

    if performance_diff >= 20:
        # Performing 2 full tiers above current rank
        estimated_mmr_index = min(current_rank_index + 2, len(RANK_ORDER) - 1)
        confidence = "High"
    elif performance_diff >= 10:
        # Performing 1 full tier above current rank
        estimated_mmr_index = min(current_rank_index + 1, len(RANK_ORDER) - 1)
        confidence = "Medium"
    elif performance_diff >= 0:
        # Performing at or slightly above current rank
        estimated_mmr_index = current_rank_index
        confidence = "High"
    elif performance_diff >= -10:
        # Performing slightly below current rank
        estimated_mmr_index = max(current_rank_index - 1, 0)
        confidence = "Medium"
    else:
        # Performing significantly below current rank
        estimated_mmr_index = max(current_rank_index - 2, 0)
        confidence = "Low"

    estimated_mmr_rank = RANK_ORDER[estimated_mmr_index]

    # Build the explanation message
    if estimated_mmr_rank == current_rank_name:
        gap_message = (
            f"Your performance aligns with your visible rank. "
            f"Your lobbies should feel fair and matched to your skill level."
        )
    elif estimated_mmr_index > current_rank_index:
        gap_message = (
            f"You are performing ABOVE your visible rank. "
            f"The game may be placing you in harder lobbies than your rank suggests. "
            f"This is normal! It means you are likely climbing and your MMR is ahead of your visible rank."
        )
    else:
        gap_message = (
            f"You are performing BELOW your visible rank. "
            f"Your lobbies may feel easier than expected. "
            f"Focus on consistency to bring your performance in line with your rank."
        )

    return {
        "visible_rank": current_rank_name,
        "estimated_mmr_rank": estimated_mmr_rank,
        "avg_net_rp_per_game": round(avg_net_rp_per_game, 1),
        "expected_avg_net_rp": expected_avg,
        "performance_diff": round(performance_diff, 1),
        "confidence": confidence,
        "gap_message": gap_message
    }