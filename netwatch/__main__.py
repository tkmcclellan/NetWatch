from argparse import ArgumentParser
from netwatch.main import run
import netwatch.messenger
import netwatch.scraper
import netwatch.ui

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--enable_gui",
        action="store_true",
        help="Starts and closes the server with the GUI",
    )
    parser.add_argument(
        "--disable_scheduler",
        action="store_true",
        help="Disables the NetWatch Alert scheduler",
    )

    parser.add_argument("--messenger", action="store_true",
                        help="Flag for using the messenger module")
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

    parser.add_argument("--scraper", action="store_true",
                        help="Flag for using the scraper module")
    parser.add_argument("--link", help="Link to page to be scraped")
    parser.add_argument(
        "--selector", help="CSS selector for portion of page to be scraped")

    parser.add_argument("--gui", action="store_true",
                        help="Starts the NetWatch GUI on its own")

    args = parser.parse_args()

    if args.messenger:
        if args.email_client == "smtp":
            netwatch.messenger.send_smtp_email(
                username=args.username,
                password=args.password,
                subject=args.subject,
                body=args.body,
                recipient=args.recipient,
                smtp_addr=args.smtp_addr,
            )
        else:
            netwatch.messenger.send_sendgrid_email(
                username=args.username,
                api_key=args.api_key,
                subject=args.subject,
                body=args.body,
                recipient=args.recipient,
                body_type="text/plain"
            )
    elif args.scraper:
        data = netwatch.scraper.fetch_site_html(netwatch.scraper.SiteData(
            id="",
            link=args.link,
            selector=args.selector
        ))[0]

        print("{} - {} - {}".format(args.link, args.selector, data.html))
    elif args.gui:
        netwatch.ui.GUI()
    else:
        run(enable_gui=args.enable_gui, disable_scheduler=args.disable_scheduler)
