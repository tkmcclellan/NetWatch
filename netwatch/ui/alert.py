import PySimpleGUI as sg

from netwatch.ui.util import *


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


def edit_window(alert):
    layout = alert_layout(alert)
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
                value=process_frequency(values))
        if event == "email":
            window["email_frame"].update(
                visible=window["email"].get() == 1)
        if event == "Save":
            if check_invalid(window, values):
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
