class Database:
    """Storage class for Notion databases."""

    def __init__(self, db_id: str, props: dict): 
        self.id = db_id;
        self.properties = props;

    def _checked(self, property: dict, value: str):
        """Checks if the property exists before outputting it."""
        if not property:
            return None
        else:
            return property.get(value)

    def _checkbox(self, property: dict):
        """Retrieves the value of a checkbox property."""
        return bool(self._checked(property, "checkbox"))

    def _created_by(self, property: dict):
        """Retrieves the value of a created_by property."""
        user = self._checked(property, "created_by")
        return self._checked(user, "id")

    def _created_time(self, property: dict):
        """Retrieves the value of a created_time property."""
        return self._checked(property, "created_time")

    def _date(self, property: dict):
        """Retrieves the value of a date property."""
        date = self._checked(property, "date")

        if not date:
            return None
        return {
            "start": date.get("start"),
            "end": date.get("end"),
            "time_zone": date.get("time_zone"),
        }

    def _email(self, property: dict):
        """Retrieves the value of an email property."""
        return self._checked(property, "email")

    def _files(self, property: dict):
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

    def _last_edited_by(self, property: dict):
        """Retrieves the value of a last_edited_by property."""
        user = self._checked(property, "last_edited_by")
        return self._checked(user, "id")

    def _last_edited_time(self, property: dict):
        """Retrieves the value of a last_edited_time property."""
        return self._checked(property, "last_edited_time")

    def _multi_select(self, property: dict):
        """Retrieves the value of a multi_select property."""
        values = self._checked(property, "multi_select")
        if not values:
            values = []

        return [v["name"] for v in values]

    def _number(self, property: dict):
        """Retrieves the value of a number property."""
        return self._checked(property, "number")

    def _people(self, property: dict):
        """Retrieves the value of a people property."""
        people = self._checked(property, "people")
        if not people:
            people = []

        return [p.get("id") for p in people]

    def _phone_number(self, property: dict):
        """Retrieves the value of a phone_number property."""
        return self._checked(property, "phone_number")

    def _place(self, property: dict):
        """Retrieves the value of a place property."""
        return self._checked(property, "place")

    def _relation(self, property: dict):
        """Retrieves the value of a relation property."""
        relations = self._checked(property, "relation")
        if not relations:
            relations = []

        return [r["id"] for r in relations]

    def _rich_text(self, property: dict):
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

    def _rollup(self, property: dict):
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

    def _select(self, property: dict):
        """Retrieves the value of a select property."""
        value = self._checked(property, "select")
        return self._checked(value, "name")

    def _status(self, property: dict):
        """Retrieves the value of a status property."""
        value = self._checked(property, "status")
        return self._checked(value, "name")

    def _title(self, property: dict):
        """Retrieves the value of a title property."""
        titles = self._checked(property, "title")
        if not titles:
            titles = []

        return " ".join(t["plain_text"] for t in titles)

    def _url(self, property: dict):
        """Retrieves the value of a URL property."""
        return self._checked(property, "url")

    def get_value(self, property: dict):
        """Retrieves the value of a property dynamically by type."""
        if not property:
            return None

        handler = getattr(self, f"_{property['type']}", None)
        if handler:
            return handler(property)
        return None
