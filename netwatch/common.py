"""Module for processing NetWatch Alerts

This module uses the messenger, scraper, and store modules
to fetch site data, compare that data against existing data
in the store, and send notifications if the website has updated.
"""

from datetime import datetime
import hashlib

import keyring

import netwatch.messenger
import netwatch.scraper
from netwatch.store import store


def process_alert(alert_ids):
    """Processes NetWatch Alerts.

    Retreives each Alert's hash/diff from the web scraper,
    checks to see if the website has changed, and sends notifications
    to those that have changed.

    Args:
        alert_ids (List[str]): List of alert ids representing
            Alerts to be processed.

    Returns:
        List[Alert]: List of Alerts that have changed.
    """

    alerts = store.get_alerts(alert_ids)
    site_data = netwatch.scraper.fetch_site_html([netwatch.scraper.SiteData(
        id=alert.id,
        link=alert.link,
        selector=alert.selector,
    ) for alert in alerts], chromedriver_path=store.get_config("chromedriver_path"))
    changed = []
    for i in range(len(alerts)):
        site_data[i].hash = hashlib.md5(site_data[i].html.encode()).hexdigest()
        if alerts[i].hash != site_data[i].hash:
            store.update_alert(id=alerts[i].id, hash=site_data[i].hash)
            store.create_update(
                text="{} :: {}: {}".format(
                    datetime.now().isoformat(), alerts[i].name, alerts[i].alert
                ),
                link=alerts[i].link,
            )
            changed.append(alerts[i])
    send_notifications(changed, sender=store.get_config("email_sender"))
    return changed


def send_notifications(alerts, sender="smtp", smtp_addr="smtp.googlemail.com"):
    """Sends email notifications using list of alerts.

    Sends email notifications using the email service represented in sender
    to the recipient of each Alert in alerts.

    Args:
        alerts: A List of Alerts.
        sender: Optional; Determines the email service used to
            send alerts. Accepts `smtp` or `sendgrid` and
            defaults to `smtp`.
        smtp_addr: Optional; Represents the SMTP address to send
            emails to.
    """

    username = store.get_config("username")
    password = keyring.get_password("netwatch_email_password", username)
    sendgrid_api_key = keyring.get_password(
        "netwatch_sendgrid_api_key", username)

    for alert in alerts:
        if alert.email:
            body = "{} - {}".format(alert.alert, alert.link)

            if sender == "smtp":
                netwatch.messenger.send_smtp_email(
                    username=store.get_config("username"),
                    password=password,
                    subject="NetWatch",
                    body=body,
                    recipient=alert.recipient,
                    smtp_addr=smtp_addr,
                )
            elif sender == "sendgrid":
                netwatch.messenger.send_sendgrid_email(
                    username=store.get_config("username"),
                    api_key=sendgrid_api_key,
                    subject="NetWatch",
                    body=body,
                    recipient=alert.recipient,
                    body_type=alert.content_type,
                )
            else:
                raise Exception("Invalid email sender config")
