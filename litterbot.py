import os
import asyncio
import pprint

from pylitterbot import Account

from datetime import datetime, timedelta, timezone
import re

def is_weight_record(action: str) -> bool:
    return action[0:19] == "Pet Weight Recorded"

def append_weight(cat_weights: list, name: str, timestamp: datetime, weight: float):
    cat_weights.append({
        "cat": name,
        "timestamp": timestamp,
        "weight_lbs": weight
    })

def get_recent_weights(activity_list) -> list:
    cutoff = datetime.now(timezone.utc) - timedelta(days=1)
    weights = []

    for activity in activity_list:
        if activity.timestamp < cutoff:
            continue

        action = activity.action
        if isinstance(action, str) and is_weight_record(action):
            match = re.search(r"([\d.]+)", action)
            if match:
                weight_lbs = float(match.group(1))
                if weight_lbs > 11.5:
                    append_weight(weights, "basmati", activity.timestamp, weight_lbs)
                else:
                    append_weight(weights, "jasmine", activity.timestamp, weight_lbs)

    return weights

async def connect(account: Account) -> int:
    try:
        await account.connect(
            username=os.environ["WHISKER_EMAIL"], 
            password=os.environ["WHISKER_PASSWORD"], 
            load_robots=True
        )

        return len(account.robots)
        robot = account.robots[0]
        return get_recent_weights(await robot.get_activity_history(limit = 10000))
    finally:
        await account.disconnect()

if __name__ == "__main__":
    asyncio.run(connect())