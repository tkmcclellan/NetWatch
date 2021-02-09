"""Module for sending messages.

This module allows for sending email and (in the near future)
text notifications with a variety of service providers.

Example:
    This module can be used from the command line and as an import.
    Command line example::

        $ python messenger.py --username e@mail.com --password 1234 \
            --body "ody ody ody" --subject Subject --recipient u@mail.com \
            --smtp_addr smtp.googlemail.com

    Import example::

        >>> import messenger
        >>> messenger.send_smtp_email(
                username="e@mail.com",
                password="1234",
                body="ody ody ody",
                subject="Subject",
                recipient="u@mail.com",
                smtp_addr="smtp.googlemail.com",
            )

Todo:
    * Add SMS gateway support
    * Add Twilio SMS support
"""

from argparse import ArgumentParser

import keyring
from envelopes import Envelope
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, To

from store import store


def send_smtp_email(username, password, subject, body, recipient, smtp_addr):
    """Sends an email using SMTP

    Sends a simple email using the SMTP protocol to a given address.

    Args:
        username (str): Sender's email username.
        password (str): Sender's email password.
        subject (str): Email subject.
        body (str): Email body.
        recipient (str): Recipient's email username.
        smtp_addr (str): SMTP address.
    """

    if not password:
        raise Exception("Missing email password")

    envelope = Envelope(
        from_addr=username, to_addr=recipient, subject=subject, text_body=body
    )

    envelope.send(
        smtp_addr,
        login=username,
        password=keyring.get_password("netwatch_email_password", username),
        tls=True,
    )


def send_sendgrid_email(username, api_key, subject, body, recipient, body_type):
    """Sends an email using SendGrid

    Sends an email using the SendGrid email service. Allows plaintext email bodies
    and HTML email bodies.

    Args:
        username (str): Sender's email address.
        api_key (str): SendGrid API key.
        subject (str): Email subject.
        body (str): Email body.
        recipient (str): Recipient's email address.
        body_type (str): Body type of email. Accepts "text/plain" and "text/html".
    """

    sg = SendGridAPIClient(api_key=api_key)
    from_email = Email(username)
    to_email = To(recipient)
    content = Content(body_type, body)
    mail = Mail(from_email, to_email, subject, content)
    sg.client.mail.send.post(request_body=mail.get())


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--email_client", help="SMTP or SendGrid", default="smtp")
    parser.add_argument("--username", help="The sender's email address")
    parser.add_argument(
        "--password", help="The sender's email password", default=None)
    parser.add_argument("--api_key", help="SendGrid API Key", default=None)
    parser.add_argument("--body", help="Email body")
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--recipient", help="Recipient email address")
    parser.add_argument(
        "--smtp_addr", help="SMTP email server address", default="smtp.googlemail.com"
    )

    args = parser.parse_args()

    if args.email_client == "smtp":
        send_smtp_email(
            username=args.username,
            password=args.password,
            subject=args.subject,
            body=args.body,
            recipient=args.recipient,
            smtp_addr=args.smtp_addr,
        )
    else:
        send_sendgrid_email(
            username=args.username,
            api_key=args.api_key,
            subject=args.subject,
            body=args.body,
            recipient=args.recipient,
            body_type="text/plain"
        )
