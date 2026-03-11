import os
import sys
from pprint import pprint
from datetime import datetime, timezone, timedelta

from notion_client import Client
from loguru import logger

from databases import TasksDatabase

def configure_logger():
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {extra}")

def main():
    client = Client(auth=os.environ["NOTION_TOKEN"])
    configure_logger()

    tasks_db = TasksDatabase(client, logger)
    tasks_db.reset_overdue_tasks()


if __name__ == "__main__":
    main()
