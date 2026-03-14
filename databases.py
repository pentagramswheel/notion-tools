from datetime import datetime, timezone, timedelta

from notion import Property
from notion_client import AsyncClient
from litterbot import Whisker

class Database:
    """A class which interacts with Notion databases."""
    def __init__(self, client: AsyncClient, db_id: str, logger):
        self.__notion_app = client
        self._id = db_id
        self._logger = logger

    def _to_date(self, dt: datetime) -> str:
        """Converts a datetime to a date.

        Args:
            dt: The datetime object.

        Returns:
            A date in the form of a string.
        """
        return dt.date().isoformat()
    
    def _to_notion_people(self, people_ids: list, indices=None) -> list:
        """Returns a list of SDK-compliant people objects to update to.

        Args:
            people: The people IDs.
            indices: Indices of people to return.

        Returns:
            The compliant version of the list.
        """
        if not people_ids:
            people_ids = []

        selected = people_ids
        
        if isinstance(indices, int):
            selected = [people_ids[indices % len(people_ids)]]
        elif isinstance(indices, list):
            selected = [people_ids[i % len(people_ids)] for i in indices]
        else:
            raise TypeError(f"indices must be int, list, or None, got {type(indices)}")

        return [{"object": "group", "id": person["id"]} for person in selected]
    
    def _get_property(self, properties: dict, key=None):
        """Retrieve a property's value via its key if any."""
        if properties and key:
            return Property(properties.get(key)).get_value()
        else:
            raise KeyError("Property could not be found.")
    
    def __all_pages(self):
        """Retrieve all Notion pages."""
        return self.__notion_app.pages
    
    def _data_sources(self):
        """Retrieve all Notion data sources."""
        return self.__notion_app.data_sources
        
    async def _create_database_page(self, new_properties: dict) -> dict:
        """Creates a Notion page within a database.

        Args:
            new_properties: The page's properties.

        Returns:
            The SDK response.
        """
        return await self.__all_pages().create(
            parent={"data_source_id": self._id},
            properties=new_properties
        )

    async def _update_database_page(self, page_key: str, updated_properties: dict) -> dict:
        """Updates a Notion page within a database.

        Args:
            page_key: The primary key/title of the page.
            updated_properties: The properties to update to.

        Returns:
            The SDK response.
        """
        return await self.__all_pages().update(
            page_id=page_key, 
            properties=updated_properties
        )
    
    async def _delete_database_page(self, page_key: str) -> dict:
        """Deletes a Notion page within a database.

        Args:
            page_key: The primary key/title of the page.
            updated_properties: The properties to update to.

        Returns:
            The SDK response.
        """
        return await self.__all_pages().update(
            page_id=page_key, 
            archived=True
        )

class TasksDatabase(Database):
    """A class which interacts with the tasks database."""

    def __init__(self, client, tasks_db_id, logger):
        super().__init__(client, tasks_db_id, logger)

    async def __overdue_tasks(self):
        """Retrieves the overdue tasks."""
        cursor = None
        cutoff = datetime.now(timezone.utc) + timedelta(hours=1)
        cutoff_iso = cutoff.isoformat()

        while True:
            response = await self._data_sources().query(
                data_source_id=self._id,
                start_cursor=cursor,
                filter={
                    "property": "deadline",
                    "date": {"before": cutoff_iso}
                }
            )

            for task in response.get("results", []):
                yield task

            if not response.get("has_more"):
                break

            cursor = response.get("next_cursor")

    async def reset_overdue_tasks(self):
        """Resets the overdue tasks."""
        updated = 0

        try:
            async for task in self.__overdue_tasks():
                props = task.get("properties", {})
                deadline = self._get_property(props, "deadline")
                if not deadline or not deadline.get("start"):
                    continue

                task_name = str(self._get_property(props, "task"))
                schedule = str(self._get_property(props, "schedule"))
                week_rot = int(self._get_property(props, "week_rot"))
                people = list(self._get_property(props, "people"))

                curr_deadline = datetime.fromisoformat(str(deadline["start"]).replace("Z", "+00:00"))
                new_deadline = curr_deadline + timedelta(weeks=week_rot)

                updated_properties = {
                    "status": {"status": {"name": "NS"}},
                    "deadline": {"date": {"start": self._to_date(new_deadline)}}
                }

                if "alt" in schedule.lower() and len(people) > 0:
                    assigned = list(Property(props.get("assigned")).get_value())
                    if assigned:
                        current_assigned = assigned[0]
                        new_index = (people.index(current_assigned) + 1) % len(people)
                        updated_properties["assigned"] = {"people": self._to_notion_people(people, new_index)}

                await self._update_database_page(task["id"], updated_properties)
                self._logger.bind(task=task_name) \
                    .info("task_updated")
                
                updated += 1
        except TypeError as e:
            self._logger.error("Type error found. Stopping reset.", e)
        except KeyError as e:
            self._logger.error("Key error found. Stopping reset.", e)

        self._logger.bind(num_tasks=updated) \
            .info("task_db_updated")
        
class LitterBotDatabase(Database):
    """A class which interacts with the tasks database."""

    def __init__(self, client, lr_db_id, logger):
        super().__init__(client, lr_db_id, logger)

    async def __old_weights(self):
        """Retrieves the overdue tasks."""
        cursor = None
        cutoff = datetime.now(timezone.utc) - timedelta(weeks=2)
        cutoff_iso = cutoff.isoformat()

        while True:
            response = await self._data_sources().query(
                data_source_id=self._id,
                start_cursor=cursor,
                filter={
                    "property": "timestamp",
                    "date": {"before": cutoff_iso}
                }
            )

            for weight in response.get("results", []):
                yield weight

            if not response.get("has_more"):
                break

            cursor = response.get("next_cursor")

    async def update_weights(self, email: str, passphrase: str):
        """Updates the cats' recent weights."""
        updated = 0
        deleted = 0
        account = Whisker()

        try:
            robots = await account.connect(email, passphrase)
            
            async for record in self.__old_weights():
                await self._delete_database_page(record["id"])
                deleted += 1

            for robot in robots:
                recent_weights = await account.get_recent_weights(robot)
                
                for weight in recent_weights:
                    await self._create_database_page(weight)
                    updated += 1
        except TypeError as e:
            self._logger.error("Type error found. Stopping reset.", e)
        except KeyError as e:
            self._logger.error("Key error found. Stopping reset.", e)
        except Exception as e:
            self._logger.error("Could not log into the Whisker account.", e)

        await account.disconnect()
        self._logger.bind(
            new_weights=updated, 
            deleted_weights=deleted) \
            .info("weights_db_updated")
    