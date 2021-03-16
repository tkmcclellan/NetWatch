import re
import traceback

import PySimpleGUI as sg
import requests
from croniter import croniter

KEYS = ["name", "description", "alert", "link", "selector"]
MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
WEEKDAYS = ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat"]


def check_invalid(window, values):
    invalid = False

    if re.search(
        "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        window["link"].get(),
    ):
        window["invalid_link"].update(visible=False)
    else:
        invalid = True
        window["invalid_link"].update(visible=True)

    if re.search(
        "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", window["recipient"].get()
    ):
        window["invalid_recipient"].update(visible=False)
    else:
        window["invalid_recipient"].update(visible=True)
        invalid = True

    if values["content_type"] in ["text/plain", "text/html"]:
        window["invalid_type"].update(visible=False)
    else:
        window["invalid_type"].update(visible=True)
        invalid = True

    if croniter.is_valid(values["frequency"]):
        window["invalid_cron"].update(visible=False)
    else:
        window["invalid_cron"].update(visible=True)
        invalid = True

    return invalid


def process_frequency(values):
    frequency = ""

    for time in ["minute", "hour", "day"]:
        combo = values["f{}".format(time)]
        value = values["f{}_input".format(time)]

        if combo == "every":
            if value in ["0", "1"]:
                frequency += "* "
            else:
                frequency += "*/{} ".format(value)
        else:
            frequency += value + " "
    try:
        month = int(values["fmonth_input"])
        if month in [0, 1]:
            frequency += "* "
        else:
            frequency += "*/{} ".format(month)
    except:
        index = MONTHS.index(values["fmonth_input"])
        frequency += str(index) + " "
    try:
        weekday = int(values["fweekday_input"])
        if weekday in [0, 1]:
            frequency += "*"
        else:
            frequency += "*/{}".format(weekday)
    except:
        index = WEEKDAYS.index(values["fweekday_input"])
        frequency += str(index)

    return frequency


def format_alerts(alerts):
    if alerts:
        return [
            alert["name"] + ' | ' + alert["description"] for alert in alerts
        ]
    else:
        return []


def format_updates(updates):
    if updates:
        return [u["text"] for u in updates]
    else:
        return []


def get_alert_id_from_index(alerts, index):
    return alerts[index]["id"]


def send(method, data, identifier=None, params=None):
    try:
        if identifier:
            r = requests.request(
                method,
                "http://localhost:9494/{}/{}".format(data, identifier),
                params=params,
            )
        else:
            r = requests.request(
                method, "http://localhost:9494/{}".format(data), params=params
            )
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        if e.response.status_code == 400:
            sg.popup(
                "Invalid Request: {}".format(e.response.url),
                title="An Error Has Occurred",
            )
    except Exception as e:
        sg.popup(
            "".join(traceback.format_exception(
                type(e), e, e.__traceback__)),
            title="An Error Has Occurred"
        )
