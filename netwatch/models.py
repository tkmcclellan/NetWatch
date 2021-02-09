"""Module for NetWatch datatypes"""

class Update:
    """Update class representing Alert updates.

    Attributes:
        text (str): The text to be displayed on the update window.
        link (str): The link to open in browser when an update is clicked.
    """

    def __init__(self, text, link):
        self.text = text
        self.link = link

    def format(self):
        """Returns a text-formatted version of an Update"""

        return "{} - {}".format(self.text, self.link)

    def to_json(self):
        """Returns an Update as a Dict"""

        return {"text": self.text, "link": self.link}


class Alert:
    """Class representing NetWatch alerts.

    This class represents the websites NetWatch tracks and
    information related to these trackers.

    Attributes:
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
    """

    def __init__(
        self,
        id,
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
        self.id = id
        self.name = name
        self.description = description
        self.alert = alert
        self.link = link
        self.selector = selector
        self.hash = hash
        self.email = email
        self.recipient = recipient
        self.content_type = content_type
        self.frequency = frequency

    def to_json(self):
        """Returns Alert as a Dict"""

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "alert": self.alert,
            "link": self.link,
            "selector": self.selector,
            "hash": self.hash,
            "email": self.email,
            "recipient": self.recipient,
            "content_type": self.content_type,
            "frequency": self.frequency,
        }
