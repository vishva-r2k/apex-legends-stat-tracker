import json
from datetime import datetime
import os

def save_to_file(data):
    # Create data folder if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Generate timestamped filename
    filename = f"data/data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Save JSON
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Saved to {filename}")