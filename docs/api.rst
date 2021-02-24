=================
NetWatch REST API
=================
Documentation for using NetWatch's REST API.

The server runs on address 127.0.0.1 and port 9494.

Resources
=========

**Alerts**
----------

GET
~~~
Returns NetWatch Alerts.

Endpoint: ``GET localhost:9494/alerts/{alert_ids}``

.. list-table:: **URI Parameters**
    :widths: 25 25 25 25 25
    :header-rows: 1

    * - Name
      - In
      - Required
      - Type
      - Description
    * - ``alert_ids``
      - path
      - False
      - string
      - Comma separated list of Alert ids representing Alerts to be returned. If this is not included, all Alerts will be returned.

.. list-table:: **Responses**
    :widths: 25 25 25
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - 200 OK
      - Alert
      - OK. Returns list of Alerts.
    * - 400
      - Error Response
      - Invalid Request

PUT
~~~
Updates NetWatch Alerts.

Endpoint: ``PUT localhost:9494/alerts/{alert_id}``

.. list-table:: **URI Parameters**
    :widths: 25 25 25 25 25
    :header-rows: 1

    * - Name
      - In
      - Required
      - Type
      - Description
    * - ``alert_id``
      - path
      - True
      - string
      - ID of Alerts to be updated.
    * - ``name``
      - query
      - False
      - string
      - The name of the Alert.
    * - ``description``
      - query
      - False
      - string
      - A short description of the Alert.
    * - ``alert``
      - query
      - False
      - string
      - The message to be sent when a website updates.
    * - ``link``
      - query
      - False
      - string
      - A link to the website this Alert points to.
    * - ``selector``
      - query
      - False
      - string
      - The HTML selector for the subsection of the website this Alert points to.
    * - ``email``
      - query
      - False
      - bool
      - Enables or disables email notifications for this Alert.
    * - ``recipient``
      - query
      - False
      - string
      - The email recipient of this Alert.
    * - ``content_type``
      - query
      - False
      - string
      - The email body content type (required for SendGrid). Valid values are "text/plain" or "text/html".
    * - ``frequency``
      - query
      - False
      - string
      - Cron formatted frequency representing how often this Alert should be processed by the scheduler.

.. list-table:: **Responses**
    :widths: 25 25 25
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - 200 OK
      - Alert
      - OK. Returns updated Alert.
    * - 400
      - Error Response
      - Invalid Request

POST
~~~~
Creates NetWatch Alerts.

Endpoint: ``POST localhost:9494/alerts``

.. list-table:: **URI Parameters**
    :widths: 25 25 25 25 25
    :header-rows: 1

    * - Name
      - In
      - Required
      - Type
      - Description
    * - ``name``
      - query
      - True
      - string
      - The name of the Alert.
    * - ``description``
      - query
      - True
      - string
      - A short description of the Alert.
    * - ``alert``
      - query
      - True
      - string
      - The message to be sent when a website updates.
    * - ``link``
      - query
      - True
      - string
      - A link to the website this Alert points to.
    * - ``selector``
      - query
      - True
      - string
      - The HTML selector for the subsection of the website this Alert points to.
    * - ``email``
      - query
      - True
      - bool
      - Enables or disables email notifications for this Alert.
    * - ``recipient``
      - query
      - True
      - string
      - The email recipient of this Alert.
    * - ``content_type``
      - query
      - True
      - string
      - The email body content type (required for SendGrid). Valid values are "text/plain" or "text/html".
    * - ``frequency``
      - query
      - True
      - string
      - Cron formatted frequency representing how often this Alert should be processed by the scheduler.

.. list-table:: **Responses**
    :widths: 25 25 25
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - 200 OK
      - Alert
      - OK. Returns newly created Alert.
    * - 400
      - Error Response
      - Invalid Request

DELETE
~~~~~~
Deletes NetWatch Alerts.

Endpoint: ``DELETE localhost:9494/alerts/{alert_id}``

.. list-table:: **URI Parameters**
    :widths: 25 25 25 25 25
    :header-rows: 1

    * - Name
      - In
      - Required
      - Type
      - Description
    * - ``alert_id``
      - path
      - True
      - string
      - ID of the Alert to be deleted.

.. list-table:: **Responses**
    :widths: 25 25 25
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - 200 OK
      - Alert
      - OK. Returns deleted Alert.
    * - 400
      - Error Response
      - Invalid Request

**Updates**
-----------

GET
~~~
Returns NetWatch Updates.

Endpoint: ``GET localhost:9494/updates``

.. list-table:: **Responses**
    :widths: 25 25 25
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - 200 OK
      - Alert
      - OK. Returns list of Updates.
    * - 400
      - Error Response
      - Invalid Request

**Config**
----------

GET
~~~
Returns NetWatch configuration.

Endpoint: ``GET localhost:9494/config``

.. list-table:: **Responses**
    :widths: 25 25 25
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - 200 OK
      - Alert
      - OK. Returns dictionary of NetWatch configurations.
    * - 400
      - Error Response
      - Invalid Request

PUT
~~~~
Updates NetWatch configuration.

Endpoint: ``PUT localhost:9494/config``

.. list-table:: **URI Parameters**
    :widths: 25 25 25 25 25
    :header-rows: 1

    * - Name
      - In
      - Required
      - Type
      - Description
    * - ``username``
      - query
      - False
      - string
      - The email address for sending outgoing emails.
    * - ``default_recipient``
      - query
      - False
      - string
      - Default email recipient of NetWatch email notifications.
    * - ``email_sender``
      - query
      - False
      - string
      - The email service to use for sending NetWatch email notifications. Valid values are ``smtp`` and ``sendgrid``.
    * - ``smtp_addr``
      - query
      - False
      - string
      - URI to send SMTP emails to.
    * - ``chromedriver_path``
      - query
      - False
      - string
      - Path to chromedriver executable.

.. list-table:: **Responses**
    :widths: 25 25 25
    :header-rows: 1

    * - Name
      - Type
      - Description
    * - 200 OK
      - Alert
      - OK.
    * - 400
      - Error Response
      - Invalid Request