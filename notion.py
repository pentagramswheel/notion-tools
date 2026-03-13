import os
from datetime import datetime
from zoneinfo import ZoneInfo

class Property:
    """A class which helps process Notion database properties."""

    _LOCAL_TZ = ZoneInfo(os.getenv("TZ", "America/Chicago"))

    def __init__(self, prop: dict):
        self.property = prop;

    def __checked(self, property: dict, value: str):
        """Checks if the property exists before outputting it."""
        if not property:
            return None
        else:
            return property.get(value)

    def __checkbox(self, property: dict) -> bool:
        """Retrieves the value of a checkbox property."""
        return bool(self._checked(property, "checkbox"))

    def __created_by(self, property: dict) -> str:
        """Retrieves the value of a created_by property."""
        user = self._checked(property, "created_by")
        return self._checked(user, "id")
    
    def __parseDateTime(self, datetime_str: str) -> datetime:
        if not datetime_str:
            return None

        if isinstance(datetime_str, datetime):
            if datetime_str.tzinfo:
                return datetime_str.astimezone(self._LOCAL_TZ)
            else:
                datetime_str.replace(tzinfo=self._LOCAL_TZ)

        if isinstance(datetime_str, str) and len(datetime_str) == 10:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d")
            return dt.replace(tzinfo=self._LOCAL_TZ)
        elif isinstance(datetime_str, str):
            dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            return dt.astimezone(self._LOCAL_TZ)
        else:
            return None

    def __created_time(self, property: dict) -> datetime:
        """Retrieves the value of a created_time property."""
        time = self._checked(property, "created_time")
        return self._parseDateTime(time)

    def __date(self, property: dict) -> dict:
        """Retrieves the value of a date property."""
        date = self._checked(property, "date")
        if not date:
            return None
        
        return {
            "start": self._parseDateTime(date.get("start")),
            "end": self._parseDateTime(date.get("end")),
            "time_zone": date.get("time_zone"),
        }

    def __email(self, property: dict) -> str:
        """Retrieves the value of an email property."""
        return str(self._checked(property, "email"))

    def __files(self, property: dict) -> list:
        """Retrieves the value of a files property."""
        files = property.get("files") if property else []
        files = self._checked(property, "files")
        if not files:
            files = []

        out = []
        for f in files:
            if f["type"] == "external":
                out.append(f["external"]["url"])
            else:
                out.append(f["file"]["url"])
        
        return out
    
    def __formula(self, property: dict):
        """Retrieves the value of a formula property."""
        formula = self._checked(property, "formula")
        if not formula:
            return None

        if "number" in formula:
            return int(formula["number"])
        elif "string" in formula:
            return str(formula["string"])
        elif "boolean" in formula:
            return bool(formula["boolean"])
        elif "date" in formula and formula["date"] is not None:
            return datetime.fromisoformat(formula["date"]["start"])
        else:
            return None

    def __last_edited_by(self, property: dict) -> str:
        """Retrieves the value of a last_edited_by property."""
        user = self._checked(property, "last_edited_by")
        return str(self._checked(user, "id"))

    def __last_edited_time(self, property: dict):
        """Retrieves the value of a last_edited_time property."""
        return self._checked(property, "last_edited_time")

    def __multi_select(self, property: dict):
        """Retrieves the value of a multi_select property."""
        values = self._checked(property, "multi_select")
        if not values:
            values = []

        return values

    def __number(self, property: dict):
        """Retrieves the value of a number property."""
        return self._checked(property, "number")

    def __people(self, property: dict) -> list:
        """Retrieves the value of a people property."""
        people = self._checked(property, "people")
        if not people:
            people = []

        return [{"id": p.get("id")} for p in people]

    def __phone_number(self, property: dict) -> str:
        """Retrieves the value of a phone_number property."""
        return str(self._checked(property, "phone_number"))

    def __place(self, property: dict):
        """Retrieves the value of a place property."""
        return self._checked(property, "place")

    def __relation(self, property: dict):
        """Retrieves the value of a relation property."""
        relations = self._checked(property, "relation")
        if not relations:
            relations = []

        return relations

    def __rich_text(self, property: dict):
        """Retrieves the value of a rich_text property."""
        texts = property.get("rich_text") if property else []
        texts = self._checked(property, "rich_text")
        if not texts:
            texts = []

        full_text = ""
        for text in texts:
            if text["href"]:
                full_text += text["href"]
            else:
                full_text += text["plain_text"]

            full_text += " "
            
        return full_text.rstrip()

    def __rollup(self, property: dict):
        """Retrieves the value of a rollup property."""
        rollup = self._checked(property, "rollup")
        if not rollup:
            return None
        if rollup["type"] == "number":
            return rollup["number"]
        elif rollup["type"] == "date":
            return rollup["date"]
        elif rollup["type"] == "array":
            return rollup["array"]
        
        return None

    def __select(self, property: dict):
        """Retrieves the value of a select property."""
        value = self._checked(property, "select")
        return self._checked(value, "name")

    def __status(self, property: dict):
        """Retrieves the value of a status property."""
        value = self._checked(property, "status")
        return self._checked(value, "name")

    def __title(self, property: dict):
        """Retrieves the value of a title property."""
        titles = self._checked(property, "title")
        if not titles:
            titles = []

        return " ".join(t["plain_text"] for t in titles)

    def __url(self, property: dict):
        """Retrieves the value of a URL property."""
        return self._checked(property, "url")

    def get_value(self):
        """Retrieves the value of a property dynamically by type."""
        handler = getattr(self, f"__{self.property['type']}", None)
        if handler:
            return handler(self.property)
        return None
