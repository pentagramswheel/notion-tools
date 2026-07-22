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

    async def get_recent_weights(self, robot: Robot, 
                                 cats: list, target_weights: list) -> list:
        """Extracts cats' recent weights from a litter robot activity list.
        
        Args:
            robot: The litter robot to extract weights from.
            cats: The cats to correspond weights to.
            target_weights: The cats' corresponding, ideal target weights.
        """
        activity_list = await robot.get_activity_history(limit = 10000)
        cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        weights = []
        prev_weights = [0 for cat in cats]

        for activity in sorted(activity_list, key=lambda x: x.timestamp):
            if activity.timestamp < cutoff:
                continue

            action = activity.action
            if isinstance(action, str) and self.__is_weight_record(action):
                match = re.search(r"([\d.]+)", action)
                if match:
                    weight_lbs = float(match.group(1))
                    
                    cat_index = None
                    if all(prev_weights):
                        cat_index = min(
                            range(len(cats)), 
                            key=lambda j: abs(prev_weights[j] - weight_lbs))
                    else:
                        for i, target_weight in enumerate(target_weights):
                            if weight_lbs > target_weight:
                                cat_index = i
                            else:
                                break

                    if cat_index is not None:
                        self.__append_notion_weight(
                            weights, cats[cat_index], activity.timestamp, weight_lbs)
                        prev_weights[cat_index] = weight_lbs

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
