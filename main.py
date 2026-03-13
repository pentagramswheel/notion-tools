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
    client = Client(auth=os.environ["NOTION_TOKEN"])
    configure_logger()

    if (not datetime.today().weekday()):
        tasks_id = os.environ["TASKS_DB_ID"]
        tasks_db = TasksDatabase(client, tasks_id, logger)
        tasks_db.reset_overdue_tasks()

    lr_db = LitterBotDatabase()

if __name__ == "__main__":
    main()
