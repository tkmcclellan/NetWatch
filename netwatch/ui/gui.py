"""
TODO: Create System Tray window that stays around after the main window is closed
TODO: Create keyboard shortcuts
TODO: Add documentation
TODO: Add ability to search repo for errors in error popup
"""

import webbrowser

import PySimpleGUI as sg

from netwatch.ui.alert import edit_window, new_window
from netwatch.ui.config import config_window
from netwatch.ui.util import *


class GUI:
    def __init__(self):
        self.alerts = send("GET", "alerts")
        self.updates = send("GET", "updates")
        self.config = send("GET", "config")
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
                                            values=format_updates(
                                                self.updates),
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
                                                [
                                                    sg.Listbox(
                                                        values=format_alerts(
                                                            self.alerts),
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
                send(
                    "POST",
                    "netwatch",
                    params={"ids": ",".join([alert["id"]
                                             for alert in self.alerts])},
                )
            if event == "Run":
                index = window["alerts_box"].GetIndexes()[0]
                send(
                    "POST",
                    "netwatch",
                    params={"ids": get_alert_id_from_index(index)},
                )
            if event == "New":
                alert = new_window()
                alert = send("POST", "alerts", params=alert)
                if alert:
                    self.alerts.append(alert)
            if event == "Edit":
                index = window["alerts_box"].GetIndexes()[0]
                alert = edit_window(self.alerts[index])
                if alert:
                    send("PUT", "alerts",
                         identifier=alert["id"], params=alert)
            if event == "Delete":
                alert_id = get_alert_id_from_index(
                    self.alerts, window["alerts_box"].GetIndexes()[0])
                send("DELETE", "alerts", identifier=alert_id)
                for alert in self.alerts:
                    if alert["id"] == alert_id:
                        self.alerts.remove(alert)
            if event == "Config":
                config = config_window(self.config)
                send("PUT", "config", params=config)
            if len(values["updates_box"]) > 0 and window["tabgroup"].Get() == "Updates":
                for update in self.updates:
                    if update["text"] == values["updates_box"][0]:
                        webbrowser.open(update["link"])
                        break

            window["alerts_box"].update(format_alerts(self.alerts))
            window["updates_box"].update(format_updates(self.updates))

        window.close()


if __name__ == "__main__":
    GUI()
