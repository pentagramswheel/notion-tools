import os
import sys
from datetime import datetime

import asyncio
from notion_client import AsyncClient
from loguru import logger

from databases import Tasks, LitterBot

def configure_logger():
    """Configures the main logger."""
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {extra}")

async def main():
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    configure_logger()

    if (not datetime.today().weekday()):
        tasks_db = Tasks(client, os.getenv("TASKS_DB_ID"), logger)
        await tasks_db.reset_overdue_tasks()

    lr_db = LitterBot(client, os.getenv("WEIGHTS_DB_ID"), logger)
    cat_names = os.getenv("CAT_NAMES").split(",")
    cat_target_weights = os.getenv("CAT_TARGET_WEIGHTS").split(",")

    await lr_db.update_weights(
        os.getenv("WHISKER_EMAIL"), 
        os.getenv("WHISKER_PASSWORD"),
        [name.strip() for name in cat_names],
        [float(target.strip()) for target in cat_target_weights])

if __name__ == "__main__":
    asyncio.run(main())
