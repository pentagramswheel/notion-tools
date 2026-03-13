import os
import asyncio

from pylitterbot import Account

async def main():
    account = Account()

    try:
        await account.connect(
            username=os.environ["WHISKER_EMAIL"], 
            password=os.environ["WHISKER_PASSWORD"], 
            load_robots=True
        )

        print(f"Robots: {account.robots}")
        robot = account.robots[0]
        # pprint.pprint(await robot.get_activity_history())
        # await robot.start_cleaning()
        
    finally:
        await account.disconnect()

if __name__ == "__main__":
    asyncio.run(main())