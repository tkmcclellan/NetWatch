========
NetWatch
========


.. image:: https://img.shields.io/pypi/v/netwatch.svg
        :target: https://pypi.python.org/pypi/netwatch

.. image:: https://readthedocs.org/projects/netwatch/badge/?version=latest
        :target: https://netwatch.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




NetWatch is a Python application for notifying you when websites update.

This system is based off of Alerts. Each Alert points to a website and contains directions on how to notify the user
if this website changes. Alerts can point to an entire web page or to a subsection of the page using CSS selectors. Alerts
can also be scheduled to check for updates using cron formatting.


* Free software: MIT license
* Documentation: `docs folder`_

.. _docs folder: https://github.com/tkmcclellan/NetWatch/tree/master/docs

Features
--------

* Diff checking of full web pages or subsections of pages.
* Email notification of changes using SMTP or SendGrid.
* Support for cron format scheduling of website checking.
* NetWatch webserver for interacting with NetWatch over a network.
* User interface written in PySimpleGUI.


Planned Features
----------------

* Support for additional webdrivers (currently only Chrome is supported).
* Support for text notifications using SMS email gateways and Twilio.
* A browser extension for creating NetWatch alerts directly through the browser.
* System tray icon for Windows.

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
