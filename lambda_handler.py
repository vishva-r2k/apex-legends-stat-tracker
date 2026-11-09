import json
import logging
from ingestion.scrapers.apex_status_api import (
    fetch_player_stats,
    parse_player_stats,
    parse_legend_stats,
    parse_rank_info
)
from ingestion.analytics.rank_predictor import predict_games
from ingestion.analytics.mmr_estimator import estimate_mmr_gap
from ingestion.processors.dynamo_save import save_to_dynamo
from ingestion.processors.s3_save import save_to_s3

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info("Lambda function started")
        
        body = json.loads(event.get("body", "{}")) if event.get("body") else event

        player_name = body.get("player_name")
        platform = body.get("platform", "PC")
        session_rp = int(body.get("session_rp", 0))
        session_games = int(body.get("session_games", 0))
        target_rank = body.get("target_rank")
        target_div = body.get("target_div", "IV")
        include_mmr = body.get("include_mmr_estimate", False)

        logger.info(f"Request received for player: {player_name} on {platform}")

        if not player_name:
            logger.warning("Missing required field: player_name")
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required field: player_name"})
            }

        data = fetch_player_stats(player_name, platform)
        if not data:
            logger.warning(f"Player not found: {player_name}")
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Player '{player_name}' not found."})
            }

        logger.info(f"Successfully fetched stats for {player_name}")

        player = parse_player_stats(data)
        legends = parse_legend_stats(data)
        rank = parse_rank_info(data)

        logger.info(f"Parsed player stats — Rank: {rank['rankName']} {rank['rankDiv']} | RP: {rank['rankScore']}")

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
            logger.info(f"Rank prediction complete — Games needed: {prediction['games_needed'] if prediction else 'N/A'}")

        mmr_estimate = None
        if include_mmr:
            mmr_estimate = estimate_mmr_gap(
                rank["rankName"],
                session_rp,
                session_games
            )
            logger.info(f"MMR estimate complete — Estimated rank: {mmr_estimate['estimated_mmr_rank'] if mmr_estimate else 'N/A'}")

        output = {
            "player": player,
            "legends": legends,
            "rank": rank,
            "prediction": prediction,
            "mmr_estimate": mmr_estimate
        }

        save_to_dynamo(output)
        logger.info("Saved to DynamoDB")

        save_to_s3(output)
        logger.info("Saved to S3")

        logger.info("Lambda function completed successfully")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(output)
        }

    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }