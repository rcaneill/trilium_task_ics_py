#!/usr/bin/env python

from _auth import (
    USR_nextcloud,
    PWD_nextcloud,
    URL_nextcloud,
    ICS,
    URL_trilium,
    TOKEN_trilium,
)

from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from datetime import datetime, timedelta

# from requests.auth import HTTPBasicAuth
import requests

from trilium_py.client import ETAPI

ea = ETAPI(URL_trilium, TOKEN_trilium)

datemin = "2023-01-01"
datemax = "2025-01-01"


def get_todos():
    """
    Return all todos from trilium
    """
    search_string_date = (
        "("
        + f"(#dueDate and #dueDate<={datemax} and #dueDate>={datemin}) or"
        + f"(#startDate and #startDate<={datemax} and #startDate>={datemin})"
        + ")"
    )
    res = ea.search_note(
        search=f"#todoItem and "
        f"{search_string_date}"
        "(note.parents.labels.todoInProgress or note.parents.labels.todoBacklog)",
    )
    return res


def event_from_todo(todo):
    e = Event(uid=str(datetime.now()).replace(" ", "-"))
    e.name = todo["title"]
    # e.extra.append(ContentLine(name="DESCRIPTION", value=todo[]))
    dates = {}
    for attr in todo["attributes"]:
        if attr["name"] in {"dueDate", "startDate", "endDate", "lengthTime"}:
            dates[attr["name"]] = attr["value"]
    print(dates)
    if "startDate" in dates:
        e.extra.append(
            ContentLine(
                name="DTSTART;VALUE=DATE", value=dates["startDate"].replace("-", "")
            )
        )
        if "endDate" in dates:
            e.extra.append(
                ContentLine(
                    name="DTEND;VALUE=DATE", value=dates["endDate"].replace("-", "")
                )
            )
        else:
            if "lengthTime" in dates and False:
                duration = "P" + dates["lengthTime"]
                e.extra.append(ContentLine(name="DURATION", value=duration))
            else:
                if "dueDate" in dates:
                    e.extra.append(
                        ContentLine(
                            name="DTEND;VALUE=DATE",
                            value=dates["dueDate"].replace("-", ""),
                        )
                    )
                else:
                    e.extra.append(
                        ContentLine(
                            name="DTEND;VALUE=DATE",
                            value=dates["startDate"].replace("-", ""),
                        )
                    )
    else:
        e.extra.append(
            ContentLine(
                name="DTEND;VALUE=DATE", value=dates["dueDate"].replace("-", "")
            )
        )
        e.extra.append(
            ContentLine(
                name="DTSTART;VALUE=DATE", value=dates["dueDate"].replace("-", "")
            )
        )
    return e


def main():
    res = get_todos()
    if res.get("status") == 500:
        raise (Exception("Error from the trilium server"))
    todos = res["results"]

    cal = Calendar()
    cal.extra.append(ContentLine("REFRESH-INTERVAL", {"VALUE": ["DURATION"]}, "PT15M"))

    for todo in todos:
        cal.events.add(event_from_todo(todo))

    with open("example.ics", "w") as f:
        f.writelines(cal)

    with open("example.ics", "rb") as f:
        r = requests.put(
            url=f"{URL_nextcloud}/remote.php/dav/files/{USR_nextcloud}/{ICS}",
            auth=(USR_nextcloud, PWD_nextcloud),
            data=f,
        )
        print(r.status_code)
        print(r.text)


if __name__ == "__main__":
    main()
