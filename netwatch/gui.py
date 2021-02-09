"""
TODO: Create System Tray window that stays around after the main window is closed
TODO: Create keyboard shortcuts
TODO: Add documentation
TODO: Break this up so it's not so long
TODO: Add ability to search repo for errors in error popup
"""

import re
import traceback
import webbrowser

import keyring
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


def set_window(window_title, text, service_name, username):
    layout = [
        [sg.Text(text), sg.Input(key="input_key")],
        [sg.Button("Set"), sg.Button("Cancel")],
        [
            sg.Text(
                "Input must not be empty",
                key="invalid_input",
                text_color="red",
                visible=False,
            )
        ],
    ]

    window = sg.Window(title=window_title, layout=layout, size=(200, 100))

    while True:
        event, values = window.read()

        if event == "Cancel" or event == sg.WINDOW_CLOSED:
            window.close()
            return
        if event == "Set":
            if len(values["input_key"]) < 1:
                window["invalid_input"].update(visible=True)
                continue
            else:
                window["invalid_input"].update(visible=False)
            keyring.set_password(service_name, username, values["input_key"])
            window.close()
            return


def config_window(config=None, force_save=False):
    layout = [
        [
            sg.Column(
                [
                    [sg.Text("Email*")],
                    [sg.Text("Default Recipient")],
                    [sg.Text("Email Provider*")],
                    [sg.Text("SMTP Email Password")],
                    [sg.Text("SendGrid API Key")],
                    [sg.Text("Email SMTP Address")],
                    [sg.Text("Chromedriver Path*")],
                ],
                element_justification="left",
            ),
            sg.Column(
                [
                    [
                        sg.Input(
                            key="username",
                            default_text=config["username"] if config else "",
                        ),
                    ],
                    [
                        sg.Input(
                            key="default_recipient",
                            default_text=config["default_recipient"] if config else "",
                        ),
                    ],
                    [
                        sg.Combo(
                            ["SMTP", "SendGrid"],
                            key="email_sender",
                            default_value=config["email_sender"] if config else "SMTP",
                        ),
                    ],
                    [sg.Button("Set", key="open_email_password_window")],
                    [sg.Button("Set", key="open_sendgrid_key_window")],
                    [
                        sg.Input(
                            key="smtp_addr",
                            default_text=config["smtp_addr"]
                            if config
                            else "smtp.googlemail.com",
                        ),
                    ],
                    [
                        sg.Input(
                            key="chromedriver_path",
                            default_text=config["chromedriver_path"] if config else "",
                        ),
                        sg.FileBrowse(key="filebrowse"),
                    ],
                ],
                element_justification="left",
            ),
        ],
        [sg.Text("* denotes required configurations")],
        [sg.Button("Save"), sg.Button("Cancel")],
        [
            sg.Text(
                "Empty Required Configuration",
                key="empty_config",
                text_color="red",
                visible=False,
            )
        ],
        [
            sg.Text(
                "Missing SMTP Email Password",
                key="missing_email_password",
                text_color="red",
                visible=False,
            )
        ],
        [
            sg.Text(
                "Missing SendGrid API key",
                key="missing_sendgrid_key",
                text_color="red",
                visible=False,
            )
        ],
    ]

    window = sg.Window(title="Configuration", layout=layout, size=(600, 300))

    while True:
        event, values = window.read()
        values.pop("filebrowse")
        if values["email_sender"]:
            values["email_sender"] = values["email_sender"].lower()

        if event == "Cancel" or event == sg.WINDOW_CLOSED:
            window.close()
            return
        invalid = False
        if None in [
            values[key] for key in ["username", "email_sender", "chromedriver_path"]
        ]:
            window["empty_config"].update(visible=True)
            invalid = True
        else:
            window["empty_config"].update(visible=False)
        if (
            values["email_sender"] == "smtp"
            and not (event == "open_email_password_window")
            and keyring.get_password("netwatch_email_password", values["username"])
            == None
        ):
            window["missing_email_password"].update(visible=True)
            invalid = True
        else:
            window["missing_email_password"].update(visible=False)
        if (
            values["email_sender"] == "sendgrid"
            and not (event == "open_sendgrid_key_window")
            and keyring.get_password("netwatch_sendgrid_api_key", values["username"])
            == None
        ):
            window["missing_sendgrid_key"].update(visible=True)
            invalid = True
        else:
            window["missing_sendgrid_key"].update(visible=False)
        if invalid:
            continue

        if event == "open_sendgrid_key_window":
            set_window(
                window_title="Set SendGrid API Key",
                text="SendGrid API Key",
                service_name="netwatch_sendgrid_api_key",
                username=values["username"],
            )
        if event == "open_email_password_window":
            set_window(
                window_title="Set SMTP Email Password",
                text="SMTP Email Password",
                service_name="netwatch_email_password",
                username=values["username"],
            )
        if event == "Save":
            window.close()
            return values


class GUI:
    def __init__(self):
        self.alerts = self.send("GET", "alerts")
        self.updates = self.send("GET", "updates")
        self.config = self.send("GET", "config")
        self.main_window()

    def main_window(self):
        layout = [
            [
                sg.TabGroup(
                    key="tabgroup",
                    layout=[
                        [
                            sg.Tab(
                                "Updates",
                                [
                                    [
                                        sg.Listbox(
                                            values=self.format_updates(),
                                            key="updates_box",
                                            enable_events=True,
                                            size=(200, 200),
                                        )
                                    ]
                                ],
                            ),
                            sg.Tab(
                                "Alerts",
                                [
                                    [
                                        sg.Column(
                                            [
                                                [sg.Button("Run All")],
                                                [sg.Button("Run")],
                                                [sg.Button("New")],
                                                [sg.Button("Edit")],
                                                [sg.Button("Delete")],
                                                [sg.Button("Config")],
                                            ],
                                            element_justification="center",
                                        ),
                                        sg.Column(
                                            [
                                                [sg.Text("Alerts")],
                                                [
                                                    sg.Text(
                                                        "Name | Description | Alert | Link | Selector | Hash | Frequency | Email | Recipient | Content Type"
                                                    )
                                                ],
                                                [
                                                    sg.Listbox(
                                                        values=self.format_alerts(),
                                                        key="alerts_box",
                                                        size=(200, 200),
                                                    )
                                                ],
                                            ],
                                            element_justification="center",
                                        ),
                                    ]
                                ],
                            ),
                        ]
                    ],
                )
            ]
        ]

        window = sg.Window(title="NetWatch", layout=layout, size=(800, 400))

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED:
                break
            if event == "Run All":
                self.send(
                    "POST",
                    "netwatch",
                    params={"ids": ",".join([alert["id"]
                                             for alert in self.alerts])},
                )
            if event == "Run":
                index = window["alerts_box"].GetIndexes()[0]
                self.send(
                    "POST",
                    "netwatch",
                    params={"ids": self.get_alert_id_from_index(index)},
                )
            if event == "New":
                alert = self.new_window()
                alert = self.send("POST", "alerts", params=alert)
                if alert:
                    self.alerts.append(alert)
            if event == "Edit":
                index = window["alerts_box"].GetIndexes()[0]
                alert = self.edit_window(self.alerts[index])
                if alert:
                    self.send("PUT", "alerts",
                              identifier=alert["id"], params=alert)
            if event == "Delete":
                alert_id = self.get_alert_id_from_index(
                    window["alerts_box"].GetIndexes()[0]
                )
                self.send("DELETE", "alerts", identifier=alert_id)
                for alert in self.alerts:
                    if alert["id"] == alert_id:
                        self.alerts.remove(alert)
            if event == "Config":
                config = config_window(self.config)
                self.send("PUT", "config", params=config)
            if len(values["updates_box"]) > 0 and window["tabgroup"].Get() == "Updates":
                for update in self.updates:
                    if update["text"] == values["updates_box"][0]:
                        webbrowser.open(update["link"])
                        break

            window["alerts_box"].update(self.format_alerts())
            window["updates_box"].update(self.format_updates())

        window.close()

    def alert_layout(self, alert=None):
        minute, hour, day, month, weekday = (
            alert["frequency"].split(" ") if alert else [
                "*", "*", "*", "*", "*"]
        )
        text_column = [[sg.Text(key.title())] for key in KEYS]
        input_column = [
            [sg.Input(key=key, default_text=None if not alert else alert[key])]
            for key in KEYS
        ]
        layout = [
            [
                sg.Column(text_column, element_justification="right"),
                sg.Column(input_column),
            ]
        ]

        layout.append([sg.Text("Frequency")])
        layout.append(
            [
                sg.Combo(
                    ["at", "every"],
                    default_value="every" if "/" in minute or minute == "*" else "at",
                    key="fminute",
                    enable_events=True,
                ),
                sg.Combo(
                    [str(i) for i in range(60)],
                    default_value="".join(re.findall("\d+", minute))
                    if minute != "*"
                    else "1",
                    key="fminute_input",
                    enable_events=True,
                ),
                sg.Text("minutes"),
            ]
        )
        layout.append(
            [
                sg.Combo(
                    ["at", "every"],
                    default_value="every" if "/" in hour or hour == "*" else "at",
                    key="fhour",
                    enable_events=True,
                ),
                sg.Combo(
                    [str(i) for i in range(24)],
                    default_value="".join(re.findall("\d+", hour))
                    if hour != "*"
                    else "1",
                    key="fhour_input",
                    enable_events=True,
                ),
                sg.Text("hours"),
            ]
        )
        layout.append(
            [
                sg.Combo(
                    ["at", "every"],
                    default_value="every" if "/" in day or day == "*" else "at",
                    key="fday",
                    enable_events=True,
                ),
                sg.Combo(
                    [str(i) for i in range(1, 32)],
                    default_value="".join(re.findall("\d+", day))
                    if day != "*"
                    else "1",
                    key="fday_input",
                    enable_events=True,
                ),
                sg.Text("days"),
            ]
        )
        layout.append(
            [
                sg.Text("every"),
                sg.Combo(
                    MONTHS,
                    default_value=MONTHS[int(
                        "".join(re.findall("\d+", month)))]
                    if month != "*"
                    else "1",
                    key="fmonth_input",
                    enable_events=True,
                ),
                sg.Text("(months)"),
            ]
        )
        layout.append(
            [
                sg.Text("every"),
                sg.Combo(
                    WEEKDAYS,
                    default_value=WEEKDAYS[int(
                        "".join(re.findall("\d+", weekday)))]
                    if weekday != "*"
                    else "1",
                    key="fweekday_input",
                    enable_events=True,
                ),
                sg.Text("(weekdays)"),
            ]
        )
        layout.append(
            [
                sg.Input(
                    key="frequency",
                    default_text="* * * * *" if not alert else alert["frequency"],
                )
            ]
        )
        layout.append(
            [
                sg.Checkbox(
                    "Email",
                    key="email",
                    default=True if not alert else alert["email"],
                    enable_events=True,
                )
            ]
        )
        layout.append(
            [
                sg.Frame(
                    title="",
                    border_width=0,
                    key="email_frame",
                    visible=True if not alert else alert["email"],
                    layout=[
                        [
                            sg.Text("Email Body Content Type",
                                    key="content_type_text"),
                            sg.Combo(
                                ["text/plain", "text/html"],
                                default_value="text/plain"
                                if not alert
                                else alert["content_type"],
                                key="content_type",
                            ),
                        ],
                        [
                            sg.Text("Recipient", key="recipient_text"),
                            sg.Input(
                                key="recipient",
                                default_text=self.config["default_recipient"]
                                if not alert
                                else alert["recipient"],
                            ),
                        ],
                    ],
                )
            ]
        )
        layout.append(
            [
                sg.Text(
                    "Invalid link url",
                    key="invalid_link",
                    visible=False,
                    text_color="red",
                )
            ]
        )
        layout.append(
            [
                sg.Text(
                    "Invalid email recipient",
                    key="invalid_recipient",
                    visible=False,
                    text_color="red",
                )
            ]
        )
        layout.append(
            [
                sg.Text(
                    "Invalid email body content type (text/plain or text/html)",
                    key="invalid_type",
                    visible=False,
                    text_color="red",
                )
            ]
        )
        layout.append(
            [
                sg.Text(
                    "Invalid schedule format",
                    key="invalid_cron",
                    visible=False,
                    text_color="red",
                )
            ]
        )
        layout.append(
            [sg.Button("Save" if alert else "Create"), sg.Button("Cancel")])

        return layout

    def check_invalid(self, window, values):
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

    def process_frequency(self, values):
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

    def edit_window(self, alert):
        layout = self.alert_layout(alert)
        window = sg.Window(title="Edit Alert", layout=layout, size=(400, 500))

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == "Cancel":
                window.close()
                break
            if event in [
                "fminute",
                "fhour",
                "fday",
                "fminute_input",
                "fhour_input",
                "fday_input",
                "fmonth_input",
                "fweekday_input",
            ]:
                window["frequency"].update(
                    value=self.process_frequency(values))
            if event == "email":
                window["email_frame"].update(
                    visible=window["email"].get() == 1)
            if event == "Save":
                if self.check_invalid(window, values):
                    continue
                for k in alert:
                    if k not in ["hash", "id"]:
                        alert[k] = values[k]
                window.close()
                return alert

    def new_window(self):
        layout = self.alert_layout()

        window = sg.Window(title="Create Alert",
                           layout=layout, size=(400, 500))

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == "Cancel":
                window.close()
                return None
            if event in [
                "fminute",
                "fhour",
                "fday",
                "fminute_input",
                "fhour_input",
                "fday_input",
                "fmonth_input",
                "fweekday_input",
            ]:
                window["frequency"].update(
                    value=self.process_frequency(values))
            if event == "email":
                window["email_frame"].update(
                    visible=window["email"].get() == 1)
            if event == "Create":
                if self.check_invalid(window, values):
                    continue

                alert = {}
                for key in KEYS:
                    alert[key] = values[key]
                alert["hash"] = ""
                alert["email"] = values["email"]
                alert["recipient"] = values["recipient"]
                alert["content_type"] = values["content_type"]
                alert["frequency"] = values["frequency"]
                window.close()
                return alert

    def send(self, method, data, identifier=None, params=None):
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

    def format_alerts(self):
        if self.alerts:
            values = [
                [str(v) for k, v in alert.items() if k != "id"] for alert in self.alerts
            ]
            return [" | ".join(v) for v in values]
        else:
            return []

    def format_updates(self):
        if self.updates:
            return [u["text"] for u in self.updates]
        else:
            return []

    def get_alert_id_from_index(self, index):
        return self.alerts[index]["id"]


if __name__ == "__main__":
    GUI()
