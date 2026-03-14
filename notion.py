import os
from typing import Any
from datetime import datetime
from zoneinfo import ZoneInfo

class Property:
    """A class which processes Notion database properties."""

    # field for local timezone
    __LOCAL_TZ: ZoneInfo = ZoneInfo(os.getenv("TZ", "America/Chicago"))
    
    def __init__(self, prop: dict):
        self.__property = prop;
    
    def __checked(self, value: str, property: dict = None):
        """Checks if the property exists before outputting it."""
        if not property:
            return self.__property.get(value)
        else:
            return property.get(value)

    def _checkbox(self) -> bool:
        """Retrieves the value of a checkbox property."""
        return bool(self.__checked("checkbox"))

    def _created_by(self) -> str:
        """Retrieves the value of a created_by property."""
        user = self.__checked("created_by")
        return self.__checked("id", user)
    
    def __parseDateTime(self, datetime_str: str) -> datetime:
        """Parses datetime strings to local timezone datetimes."""
        if not datetime_str:
            return None

        if isinstance(datetime_str, str) and len(datetime_str) == 10:
            dt = datetime.strptime(datetime_str, "%Y-%m-%d")
            return dt.replace(tzinfo=self.__LOCAL_TZ)
        elif isinstance(datetime_str, str):
            dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            return dt.astimezone(self.__LOCAL_TZ)
        else:
            return None

    def _created_time(self) -> datetime:
        """Retrieves the value of a created_time property."""
        time = self.__checked("created_time")
        return self._parseDateTime(time)

    def _date(self) -> dict:
        """Retrieves the value of a date property."""
        date = self.__checked("date")
        if not date:
            return None
        
        return {
            "start": self.__parseDateTime(date.get("start")),
            "end": self.__parseDateTime(date.get("end")),
            "time_zone": date.get("time_zone"),
        }

    def _email(self) -> str:
        """Retrieves the value of an email property."""
        return self.__checked("email")

    def _files(self) -> list:
        """Retrieves the value of a files property."""
        files = self.__checked("files")
        if not files:
            files = []

        out = []
        for f in files:
            if f["type"] == "external":
                out.append(f["external"]["url"])
            else:
                out.append(f["file"]["url"])
        
        return out
    
    def _formula(self) -> Any:
        """Retrieves the value of a formula property."""
        formula = self.__checked("formula")
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

    def _last_edited_by(self) -> str:
        """Retrieves the value of a last_edited_by property."""
        user = self.__checked("last_edited_by")
        return self.__checked("id", user)

    def _last_edited_time(self):
        """Retrieves the value of a last_edited_time property."""
        return self.__checked("last_edited_time")

    def _multi_select(self) -> list:
        """Retrieves the value of a multi_select property."""
        values = self.__checked("multi_select")
        if not values:
            values = []

        return values

    def _number(self) -> int:
        """Retrieves the value of a number property."""
        return self.__checked("number")

    def _people(self) -> list:
        """Retrieves the value of a people property."""
        people = self.__checked("people")
        if not people:
            people = []

        return [{"id": p.get("id")} for p in people]

    def _phone_number(self) -> str:
        """Retrieves the value of a phone_number property."""
        return self.__checked("phone_number")

    def _place(self):
        """Retrieves the value of a place property."""
        return self.__checked("place")

    def _relation(self) -> list:
        """Retrieves the value of a relation property."""
        relations = self.__checked("relation")
        if not relations:
            relations = []

        return relations

    def _rich_text(self) -> str:
        """Retrieves the value of a rich_text property."""
        texts = self.__checked("rich_text")
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

    def _rollup(self) -> Any:
        """Retrieves the value of a rollup property."""
        rollup = self.__checked("rollup")

        if not rollup:
            return None
        if rollup["type"] == "number":
            return rollup["number"]
        elif rollup["type"] == "date":
            return rollup["date"]
        elif rollup["type"] == "array":
            return rollup["array"]
        
        return None

    def _select(self) -> str:
        """Retrieves the value of a select property."""
        value = self.__checked("select")
        return self.__checked("name", value)

    def _status(self) -> str:
        """Retrieves the value of a status property."""
        value = self.__checked("status")
        return self.__checked("name", value)

    def _title(self) -> str:
        """Retrieves the value of a title property."""
        titles = self.__checked("title")
        if not titles:
            titles = []

        return " ".join(t["plain_text"] for t in titles)

    def _url(self):
        """Retrieves the value of a URL property."""
        return self.__checked("url")

    @property
    def value(self):
        """Retrieves the value of a property dynamically by type."""
        handler = getattr(self, f"_{self.__property['type']}")
        return handler()
