import keyring
import PySimpleGUI as sg

from netwatch.ui.util import *


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
