.. highlight:: shell

============
Installation
============


Stable release
--------------

To install NetWatch, run this command in your terminal:

.. code-block:: console

    $ pip install netwatch

This is the preferred method to install NetWatch, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for NetWatch can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/tkmcclellan/netwatch

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/tkmcclellan/netwatch/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/tkmcclellan/netwatch
.. _tarball: https://github.com/tkmcclellan/netwatch/tarball/master

Selenium
--------

NetWatch is based on the Selenium webdriver for Chrome and requires the Chrome webdriver.
This driver can be downloaded `here`_.

.. _here: https://chromedriver.chromium.org/downloads

Sending Emails
--------------

To send emails with NetWatch, you need an email account that can be accessed over
SMTP with just a username and password or a SendGrid account.
A Gmail account can be configured to do this by following `this`_ guide, and a SendGrid account
can be created at this `link`_.

.. _this: https://realpython.com/python-send-email/#option-1-setting-up-a-gmail-account-for-development
.. _link: https://signup.sendgrid.com/