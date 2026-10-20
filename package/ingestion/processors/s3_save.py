import boto3
import csv
import io
import json
from datetime import datetime

s3 = boto3.client("s3", region_name="us-east-1")
BUCKET_NAME = "als-stat-tracker-data"

def flatten_data(data):
    """
    QuickSight needs flat CSV data so we flatten the nested JSON
    into a single row with all the fields we care about.
    """
    player = data.get("player", {})
    rank = data.get("rank", {})
    prediction = data.get("prediction", {}) or {}
    mmr_estimate = data.get("mmr_estimate", {}) or {}

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "player_name": player.get("name"),
        "platform": player.get("platform"),
        "level": player.get("level"),
        "total_kills": player.get("kills"),
        "total_damage": player.get("damage"),
        "rank_name": rank.get("rankName"),
        "rank_div": rank.get("rankDiv"),
        "rank_score": rank.get("rankScore"),
        "entry_cost_per_game": prediction.get("entry_cost_per_game"),
        "avg_gross_rp_per_game": prediction.get("avg_gross_rp_per_game"),
        "avg_net_rp_per_game": prediction.get("avg_net_rp_per_game"),
        "rp_needed": prediction.get("rp_needed"),
        "games_needed": prediction.get("games_needed"),
        "visible_rank": mmr_estimate.get("visible_rank"),
        "estimated_mmr_rank": mmr_estimate.get("estimated_mmr_rank"),
        "performance_diff": mmr_estimate.get("performance_diff"),
        "mmr_confidence": mmr_estimate.get("confidence")
    }

def save_to_s3(data):
    try:
        player_name = data.get("player", {}).get("name", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Flatten the nested data into a single CSV row
        flat_data = flatten_data(data)

        # Write to an in-memory CSV buffer
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=flat_data.keys())
        writer.writeheader()
        writer.writerow(flat_data)

        # Save to S3 under sessions/player_name/timestamp.csv
        key = f"sessions/{player_name}/{timestamp}.csv"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=buffer.getvalue(),
            ContentType="text/csv"
        )

        print(f"Saved to S3: {key}")

    except Exception as e:
        print(f"Error saving to S3: {e}")