import boto3
import json
from datetime import datetime
from decimal import Decimal

# Connect to DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("ALSPlayerSessions")

def clean_for_dynamo(data):
    """
    DynamoDB does not accept float values so we convert them to Decimal.
    Also handles nested dictionaries and lists.
    """
    if isinstance(data, list):
        return [clean_for_dynamo(i) for i in data]
    elif isinstance(data, dict):
        return {k: clean_for_dynamo(v) for k, v in data.items()}
    elif isinstance(data, float):
        return Decimal(str(data))
    elif data is None:
        return "null"
    else:
        return data

def save_to_dynamo(data):
    """
    Saves a player session to DynamoDB.
    Uses player name and timestamp as the composite key.
    """
    try:
        player_name = data.get("player", {}).get("name", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        item = {
            "player_name": player_name,
            "timestamp": timestamp,
            **clean_for_dynamo(data)
        }

        table.put_item(Item=item)
        print(f"Saved to DynamoDB: {player_name} at {timestamp}")

    except Exception as e:
        print(f"Error saving to DynamoDB: {e}")