from datetime import datetime, timezone, timedelta

from notion import Property

class Database:
    """A class which interacts with Notion databases."""
    def __init__(self, client, db_id, logger):
        self.notion_app = client
        self.id = db_id
        self.logger = logger

    def to_date(self, dt: datetime) -> str:
        """Converts a datetime to a date.

        Args:
            dt: The datetime object.

        Returns:
            A date in the form of a string.
        """
        return dt.date().isoformat()

    def update_database(self, page_key: str, updated_properties: dict) -> dict:
        """Updates a Notion page within a database.

        Args:
            page_key: The primary key/title of the page.
            updated_properties: The properties to update to.

        Returns:
            The SDK response.
        """
        response = self.notion_app.pages.update(
            page_id=page_key, 
            properties=updated_properties)
        
        return response

class TasksDatabase(Database):
    """A class which interacts with the tasks database."""

    def __init__(self, client, tasks_db_id, logger):
        super().__init__(client, tasks_db_id, logger)

    def overdue_tasks(self):
        """Retrieves the overdue tasks."""
        start_cursor = None
        cutoff = datetime.now(timezone.utc) + timedelta(hours=1)
        cutoff_iso = cutoff.isoformat()

        while True:
            response = self.notion_app.data_sources.query(
                data_source_id=self.id,
                start_cursor=start_cursor,
                filter={
                    "property": "deadline",
                    "date": {"before": cutoff_iso}
                }
            )

            for task in response.get("results", []):
                yield task

            if not response.get("has_more"):
                break

            start_cursor = response.get("next_cursor")

    def reset_overdue_tasks(self):
        """Resets the overdue tasks."""
        updated = 0

        for task in self.overdue_tasks():
            props = task.get("properties", {})
            deadline = Property(props.get("deadline")).get_value()
            if not deadline or not deadline.get("start"):
                continue

            task_name = str(Property(props.get("task")).get_value())
            schedule = str(Property(props.get("schedule")).get_value())
            week_rot = int(Property(props.get("week_rot")).get_value())
            people = list(Property(props.get("people")).get_value())

            curr_deadline = datetime.fromisoformat(str(deadline["start"]).replace("Z", "+00:00"))
            new_deadline = curr_deadline + timedelta(weeks=week_rot)

            updated_properties = {
                "status": {"status": {"name": "NS"}},
                "deadline": {"date": {"start": new_deadline.date().isoformat()}}
            }

            if "alt" in schedule.lower() and len(people) > 0:
                assigned = list(Property(props.get("assigned")).get_value())
                if assigned:
                    current_assigned = assigned[0]
                    new_index = (people.index(current_assigned) + 1) % len(people)
                    updated_properties["assigned"] = {"people": [people[new_index]]}

            self.update_database(task["id"], updated_properties)
            self.logger.bind(task=task_name) \
                .info("task_updated")
            
            updated += 1

        self.logger.bind(num_tasks=updated) \
            .info("db_updated")
    