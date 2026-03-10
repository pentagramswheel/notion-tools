import os
from pprint import pprint
from datetime import datetime, timezone, timedelta
from notion_client import Client

from notiondatabase import Property

TASKS_DB_ID = os.environ["TASKS_DB_ID"]
NOTION = Client(auth=os.environ["NOTION_TOKEN"])

def overdue_tasks(cutoff_iso: str):
    start_cursor = None

    while True:
        response = NOTION.data_sources.query(
            data_source_id=TASKS_DB_ID,
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

def reset_overdue_tasks():
    updated = 0
    cutoff = datetime.now(timezone.utc) + timedelta(hours=1)
    cutoff_iso = cutoff.isoformat()

    for task in overdue_tasks(cutoff_iso):
        props = task.get("properties", {})
        deadline = Property(props.get("deadline")).get_value()
        if not deadline or not deadline.get("start"):
            continue

        task_name = Property(props.get("task")).get_value()
        schedule = Property(props.get("schedule")).get_value()
        week_rot = Property(props.get("week_rot")).get_value()
        index = Property(props.get("index")).get_value()
        people = Property(props.get("people")).get_value()

        curr_deadline = datetime.fromisoformat(str(deadline["start"]).replace("Z", "+00:00"))
        new_deadline = curr_deadline + timedelta(weeks=week_rot)

        update_payload = {
            "status": {"status": {"name": "NS"}},
            "deadline": {"date": {"start": new_deadline.date().isoformat()}}
        }

        if "alt" in str(schedule).lower() and len(people) > 0:
            new_index = (int(index) + 1) % len(people)
            update_payload["index"] = {"number": new_index}
            update_payload["assigned"] = {"people": [people[new_index]]}

        NOTION.pages.update(page_id=task["id"], properties=update_payload)
        print(f"{task_name} task updated.")
        updated += 1

    return updated

def main():
    print(f"{reset_overdue_tasks()} tasks were reset.")


if __name__ == "__main__":
    main()
