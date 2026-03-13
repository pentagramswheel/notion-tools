import os
import sys
from datetime import datetime

from notion_client import Client
from loguru import logger

from databases import TasksDatabase, LitterBotDatabase

def configure_logger():
    """Configures the main logger."""
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {extra}")

def main():
    client = Client(auth=os.getenv("NOTION_TOKEN"))
    configure_logger()

    if (not datetime.today().weekday()):
        tasks_db = TasksDatabase(client, os.getenv("TASKS_DB_ID"), logger)
        tasks_db.reset_overdue_tasks()

    lr_db = LitterBotDatabase(client, os.getenv("WEIGHTS_DB_ID"), logger)
    await lr_db.update_weights(os.getenv("WHISKER_EMAIL"), os.getenv("WHISKER_PASSWORD")) #

if __name__ == "__main__":
    main()
