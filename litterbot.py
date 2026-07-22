from datetime import datetime, timedelta, timezone
import re

from pylitterbot import Account, Robot

class Whisker:
    """A class which interacts with Whisker Litter Robots."""

    def __init__(self):
        self.__account = Account()

    def __is_weight_record(self, action: str) -> bool:
        """Checks if an activity was a weight record.

        Args:
            actions: The activity's specific action.

        Returns:
            True if a weight was recorded.
            False otherwise.
        """
        return action[0:19] == "Pet Weight Recorded"

    def __append_notion_weight(self, cat_weights: list, name: str, 
                               timestamp: datetime, weight_lbs: float):
        """Appends a weight to a list of weights in a Notion format.

        Args:
            cat_weights: The list of weights.
            name: The name of the cat.
            timestamp: The timestamp of the weight record.
            weight_lbs: The weight in lbs.
        """
        cat_weights.append({
            "cat": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            },
            "timestamp": {
                "date": {
                    "start": timestamp.isoformat()
                }
            },
            "weight": {
                "number": weight_lbs
            }
        })

    async def get_recent_weights(self, robot: Robot) -> list:
        """Extracts the recent weights from a litter robot activity list."""
        activity_list = await robot.get_activity_history(limit = 10000)
        cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        weights = []
        bas_weight, jas_weight = 0, 0

        for activity in sorted(activity_list, key=lambda x: x.timestamp):
            if activity.timestamp < cutoff:
                continue

            action = activity.action
            if isinstance(action, str) and self.__is_weight_record(action):
                match = re.search(r"([\d.]+)", action)
                if match:
                    weight_lbs = float(match.group(1))
                    bas_distance = abs(bas_weight - weight_lbs)
                    jas_distance = abs(jas_weight - weight_lbs)

                    cat = "Jasmine"
                    if bas_weight and jas_weight:
                        if bas_distance < jas_distance:
                            cat = "Basmati"
                    elif weight_lbs > 11:
                        cat = "Basmati"
                    elif weight_lbs <= 8.5:
                        cat = None

                    if cat:
                        self.__append_notion_weight(
                            weights, cat, activity.timestamp, weight_lbs)
                        
                        if cat == "Basmati":
                            bas_weight = weight_lbs
                        else:
                            jas_weight = weight_lbs

        return weights

    async def connect(self, email: str, passphrase: str) -> list:
        """Attempts a connection to the Whisker account.

        Args:
            email: The email of the account.
            passphrase: The password of the account.

        Returns:
            The list of robots attached to the account.
        """
        await self.__account.connect(
            username=email, 
            password=passphrase, 
            load_robots=True
        )

        return self.__account.robots
    
    async def disconnect(self):
        """Disconnects from the Whisker account."""
        await self.__account.disconnect()