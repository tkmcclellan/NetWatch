"""Module for retrieving HTML from static and dynamic websites.

Example:
    This module can be used as a standalone module or as an import.
    Standalone example::

        $ python scraper.py --link https://google.com --selector div 

    Import example::

        >>> import scraper
        >>> scraper.fetch_site_html(scraper.SiteData(
                    id="fakeid",
                    link="https://google.com",
                    selector="div",
                )
            )

Todo:
    * Add support for other browsers
"""

from argparse import ArgumentParser
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

from store import store

class SiteData:    
    def __init__(self, id, link, selector="", html=None, hash=None):
        self.id = id
        self.link = link
        self.selector = selector
        self.html = html
        self.hash = hash


def initialize_driver(chromedriver_path, driver_options):
    """Creates and returns a Selenium webdriver.

    Args:
        chromedriver_path (str): Path pointing to chromedriver.exe location.
        driver_options (List[str]): List of options for the chromedriver.

    Returns:
        selenium.webdriver: Initialized webdriver.
    """

    options = Options()

    for option in driver_options:
        options.add_argument(option)
    options.add_experimental_option(
        "excludeSwitches", ["enable-logging"])  # disables logging
    driver = webdriver.Chrome(
        options=options, executable_path=chromedriver_path)
    driver.set_page_load_timeout(30)
    return driver


def fetch_site_html(
    site_data,
    chromedriver_path,
    driver_options=["--headless", "--window-size=1920x1080"],
):
    """Processes NetWatch Alerts using the Selenium webdriver.

    Retreives the HTML from each Alert's linked website and creates a
    MD5 hash from that HTML.

    Args:
        site_data (List[Dict]): Single/List of SiteData object(s).
        chromedriver_path (str): Optional; Path to chromdriver.exe.
        driver_options (List[str]): Optional; List of driver options.

    Returns:
        List[SiteData]: List of Dicts containing an id corresponding to
            a NetWatch Alert and its corresponding HTML.
    """

    if not isinstance(site_data, list):
        site_data = [site_data]
    driver = initialize_driver(chromedriver_path, driver_options)

    for data in site_data:
        try:
            driver.get(data.link)
            driver.implicitly_wait(100)
            if len(data.selector) > 0:
                data.html = driver.find_element_by_css_selector(
                    data.selector
                ).get_attribute("innerHTML")
            else:
                data.html = driver.page_source
        except TimeoutException as e:
            print("Page load timeout occurred, reloading driver", e)
            driver.service.process.kill()
            driver.close()
            driver = initialize_driver(chromedriver_path, driver_options)
    driver.close()
    return site_data


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--link")
    parser.add_argument("--selector")
    args = parser.parse_args()

    data = fetch_site_html(SiteData(
        id="",
        link=args.link,
        selector=args.selector
    ))[0]

    print("{} - {} - {}".format(args.link, args.selector, data.html))
