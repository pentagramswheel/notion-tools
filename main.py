import os
import sys

from notion_client import Client
from loguru import logger

from databases import TasksDatabase

def configure_logger():
    """Configures the main logger."""
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {extra}")

def main():
    client = Client(auth=os.environ["NOTION_TOKEN"])
    tasks_id = os.environ["TASKS_DB_ID"]
    configure_logger()

    tasks_db = TasksDatabase(client, tasks_id, logger)
    tasks_db.reset_overdue_tasks()

if __name__ == "__main__":
    main()
