"""Module for managing NetWatch data.

This module loads, saves, and allows thread-safe access
and manipulation of NetWatch updates and alerts.

Attributes:
    UPDATES_FILENAME (str): Filename for NetWatch Updates.
    ALERTS_FILENAME (str): Filename for NetWatch Alerts.
    CONFIG_FILENAME (str): Filename for NetWatch configuration.
    store (Store): Singleton instance of datastore.

Todo:
    * Make configuration more robust.
"""

import json
import os
from copy import deepcopy
from secrets import token_hex
from threading import Lock

from netwatch.models import Alert, Update


UPDATES_FILENAME = r"netwatch/data/updates.json"
ALERTS_FILENAME = r"netwatch/data/alerts.json"
CONFIG_FILENAME = r"netwatch/data/config.json"


class Store:
    """Datastore for NetWatch.

    Store is a singleton class that manages data for NetWatch
    in a thread-safe manner.

    Attributes:
        updates (List[Update]): NetWatch updates.
        alerts (Dict{id: Alert}): NetWatch alerts.
        config (Dict): Configuration settings for NetWatch.
        lock (threading.Lock): Threading lock for accessing
            NetWatch data.
    """

    def __init__(self):
        if "data" not in os.listdir("netwatch"):
            os.mkdir("data")
        self.updates = [
            Update(i["text"], i["link"]) for i in _read_json(UPDATES_FILENAME, [])
        ]
        self.alerts = {
            alert_id: Alert(**alert)
            for alert_id, alert in _read_json(ALERTS_FILENAME, {}).items()
        }
        self.config = _read_json(CONFIG_FILENAME, {})
        self.lock = Lock()

    def get_alerts(self, alert_ids=None):
        """Retrieves Alerts

        Retrieves Alerts in a thread-safe manner. alert_ids is an
        optional parameter that, when not empty, returns a list of
        Alerts that correspond to the alert ids in alert_ids. If
        alert_ids is None, all alerts will be returned in a List.

        Args:
            alert_ids (List[str]): Optional; List of alert ids representing
                alerts to be returned.

        Returns:
            List[Alert]: Full or partial list of Alerts.
        """

        vals = None
        with self.lock:
            if alert_ids:
                if isinstance(alert_ids, list):
                    vals = [deepcopy(self.alerts[alert_id])
                            for alert_id in alert_ids]
                else:
                    vals = deepcopy(self.alerts[alert_ids])
            else:
                vals = list(self.alerts.values())
        return vals

    def create_alert(
        self,
        name,
        description,
        alert,
        link,
        selector,
        hash,
        email,
        recipient,
        content_type,
        frequency,
    ):
        """Creates an Alert.

        Creates a NetWatch Alert and inserts it into the store's list
        of Alerts in a thread-safe manner.

        Args:
            id (str): Unique hex token key.
            name (str): The name of the Alert.
            description (str): A short description of the Alert.
            alert (str): The message to be sent in the case a
                website updates.
            link (str): A link to the website this Alert
                points to.
            selector (str): The HTML selector for the subsection
                of the website this Alert points to.
            hash (str): A MD5 hash of the contents of this Alert's
                website.
            email (bool): Enables or disables email notifications.
            recipient (str): The recipient of the Alert.
            content_type (str): Optional; The email body content
                type (required for SendGrid). Valid values are
                "text/plain" or "text/html".
            frequency (str): Cron formatted frequency representing
                how often this Alert should be processed by the
                scheduler.

        Returns:
            Alert: Deep copy of newly created Alert.
        """

        alert_id = token_hex(16)
        alert = Alert(
            id=alert_id,
            name=name,
            description=description,
            alert=alert,
            link=link,
            selector=selector,
            hash=hash,
            email=email,
            recipient=recipient,
            content_type=content_type,
            frequency=frequency,
        )
        with self.lock:
            self.alerts[alert_id] = alert
        return deepcopy(alert)

    def update_alert(self, id, **kwargs):
        """Updates alert in store list.

        Args:
            id (str): Id of Alert to be updated.
            kwargs (Dict): Dict of Alert values to be updated.

        Returns:
            Alert: Deep copy of updated Alert.
        """

        alert = None
        with self.lock:
            for (
                key,
                value,
            ) in kwargs.items():
                if hasattr(self.alerts[id], key):
                    setattr(self.alerts[id], key, value)
                else:
                    raise Exception("Invalid Alert attribute")
            alert = deepcopy(self.alerts[id])
        return alert

    def delete_alert(self, alert_id):
        """Removes an Alert from the store.

        Args:
            alert_id (str): Id of Alert to be removed.

        Returns:
            Alert: Removed Alert.
        """

        alert = None
        with self.lock:
            alert = self.alerts.pop(alert_id)
        return alert

    def get_updates(self):
        """Returns store updates"""

        return self.updates

    def create_update(self, text, link):
        """Creates an Update.

        Args:
            text (str): Text to be displayed in the Update.
            link (str): Link to corresponding Alert's website.

        Returns:
            Update: Newly created Update.
        """

        update = Update(text, link)
        with self.lock:
            self.updates.insert(0, update)
            self.updates = self.updates[0:500]
        return update

    def get_config(self, key=None):
        """Returns NetWatch configurations.

        Returns one or all NetWatch configuration values. If `key` is
        not included, all config values will be returned.

        Args:
            key (str): Optional; Key corresponding to config value
                to be returned.

        Returns:
            str or List[str]: Specified config value(s).
        """

        value = None
        with self.lock:
            if key:
                value = deepcopy(self.config[key])
            else:
                value = deepcopy(self.config)
        return value

    def update_config(self, new_setting=False, **kwargs):
        """Updates NetWatch configuration.

        Args:
            kkwargs (Dict): Dict of configs to be updated.
            new_setting (bool): Optional; If true, set key without
                checking for its existence.
        """

        with self.lock:
            for key, value in kwargs.items():
                if key in self.config or new_setting:
                    self.config[key] = value

    def save(self):
        """Saves store data to file"""

        with self.lock:
            _write_json(
                {alert_id: alert.to_json()
                 for alert_id, alert in self.alerts.items()},
                ALERTS_FILENAME,
            )
            _write_json([update.to_json()
                         for update in self.updates], UPDATES_FILENAME)
            _write_json(self.config, CONFIG_FILENAME)


def _read_json(filename, default=[]):
    data = default
    try:
        with open(filename, "r") as file:
            file_contents = file.read()
            if len(file_contents) > 0:
                data = json.loads(file_contents)
    except FileNotFoundError:
        open(filename, "w+").close()
    return data


def _write_json(data, filename):
    with open(filename, "w") as file:
        file.write(json.dumps(data))


store = Store()
