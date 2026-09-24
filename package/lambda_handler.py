from ingestion.scrapers.apex_status_api import (
    fetch_player_stats,
    parse_player_stats,
    parse_legend_stats,
    parse_rank_info
)
from ingestion.analytics.rank_predictor import predict_games
from ingestion.analytics.mmr_estimator import estimate_mmr_gap
from ingestion.processors.dynamo_save import save_to_dynamo

import json

def lambda_handler(event, context):
    try:
        # Parse the body from API Gateway
        body = json.loads(event.get("body", "{}"))

        player_name = event.get("player_name")
        platform = event.get("platform", "PC")
        session_rp = int(event.get("session_rp", 0))
        session_games = int(event.get("session_games", 0))
        target_rank = event.get("target_rank")
        target_div = event.get("target_div", "IV")
        include_mmr = event.get("include_mmr_estimate", False)

        if not player_name:
            return {
                "statusCode": 400,
                "body": "Missing required field: player_name"
            }

        data = fetch_player_stats(player_name, platform)
        if not data:
            return {
                "statusCode": 404,
                "body": f"Player '{player_name}' not found."
            }

        player = parse_player_stats(data)
        legends = parse_legend_stats(data)
        rank = parse_rank_info(data)

        if target_rank and target_rank.lower() in ["master", "masters"]:
            target_rank = "Masters"
            target_div = "I"

        prediction = None
        if target_rank and target_div:
            prediction = predict_games(
                rank["rankScore"],
                session_rp,
                session_games,
                rank["rankName"],
                target_rank,
                target_div
            )

        mmr_estimate = None
        if include_mmr:
            mmr_estimate = estimate_mmr_gap(
                rank["rankName"],
                session_rp,
                session_games
            )

        output = {
            "player": player,
            "legends": legends,
            "rank": rank,
            "prediction": prediction,
            "mmr_estimate": mmr_estimate
        }

        save_to_dynamo(output)

        return {
            "statusCode": 200,
            "body": output
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Internal error: {str(e)}"
        }