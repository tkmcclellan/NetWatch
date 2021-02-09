"""Module for accessing NetWatch functionality over HTTP.

This module provides an HTTP interface for interacting with NetWatch.
This allows anything that can issue HTTP requests to work with 
NetWatch, be that a website, browser extension, standalone GUI, 
or even a command line utility like cURL. Full API documentation
can be found on the NetWatch GitHub repository under the `docs`
folder.

Todo:
    * Add proper error handling and param checking to API.
"""

import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from common import process_alert
from store import store


class _MyHandler(SimpleHTTPRequestHandler):
    def process_url(self):
        parsed = urlparse(
            "{}:{}{}".format(
                self.client_address[0], self.client_address[1], self.path)
        )
        split_path = parsed.path.split("/")[1:]
        datatype = split_path[0]
        identifier = None if len(split_path) < 2 else split_path[1]
        queries = parse_qs(parsed.query)
        return datatype, identifier, queries

    def default_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "json")
        self.end_headers()

    def do_GET(self):
        datatype, identifier, queries = self.process_url()

        if datatype == "alerts":
            self.default_headers()
            alerts = [
                alert.to_json()
                for alert in store.get_alerts(
                    identifier.split(",") if identifier else None
                )
            ]
            self.wfile.write(bytes(json.dumps(alerts), "utf-8"))
            return
        elif datatype == "updates":
            self.default_headers()
            self.wfile.write(
                bytes(
                    json.dumps([update.to_json()
                                for update in store.get_updates()]),
                    "utf-8",
                )
            )
            return
        elif datatype == "config":
            self.default_headers()
            self.wfile.write(bytes(json.dumps(store.get_config()), "utf-8"))
            return

        self.send_response(400, "Invalid Request")
        self.end_headers()

    def do_PUT(self):
        datatype, identifier, queries = self.process_url()

        if datatype == "alerts":
            self.default_headers()
            if "id" in queries:
                queries.pop("id")
            alert = store.update_alert(
                identifier,
                **{
                    key: bool(value[0]) if value[0] in [
                        "False", "True"] else value[0]
                    for key, value in queries.items()
                }
            )
            self.wfile.write(bytes(json.dumps(alert.to_json()), "utf-8"))
            return
        elif datatype == "config":
            self.default_headers()
            store.update_config(**queries)
            self.wfile.write(bytes("[]", "utf-8"))
            return

        self.send_response(400, "Invalid Request")
        self.end_headers()

    def do_DELETE(self):
        datatype, identifier, queries = self.process_url()

        if datatype == "alerts":
            self.default_headers()
            alert = store.delete_alert(identifier)
            self.wfile.write(bytes(json.dumps(alert.to_json()), "utf-8"))
            return

        self.send_response(400, "Invalid Request")
        self.end_headers()

    def do_POST(self):
        datatype, identifier, queries = self.process_url()

        if datatype == "netwatch":
            self.default_headers()
            alerts = process_alert(queries["ids"][0].split(","))
            self.wfile.write(
                bytes(json.dumps([alert.to_json()
                                  for alert in alerts]), "utf-8")
            )
            return
        elif datatype == "alerts":
            self.default_headers()
            alert = store.create_alert(
                name=queries["name"][0],
                description=queries["description"][0],
                alert=queries["alert"][0],
                link=queries["link"][0],
                selector=queries["selector"][0],
                hash="",
                email=bool(queries["email"][0]),
                recipient=queries["recipient"][0],
                content_type=queries["content_type"][0],
                frequency=queries["frequency"][0],
            )
            self.wfile.write(bytes(json.dumps(alert.to_json()), "utf-8"))
            return

        self.send_response(400, "Invalid Request")
        self.end_headers()


class Server:
    """A simple HTTP server for handling NetWatch requests.

    A HTTP server built off of the Standard Library http.server
    class. See API documentation for more info.

    Attributes:
        server (HTTPServer): http.server instance.
        thread (Thread): Thread for running server_handler
    """

    def __init__(self, host_name="localhost", port_number=9494):
        """Initializer for Server.

        Args:
            host_name (str): Optional; Host name for HTTP server.
            port_number (int): Optional; Port number for HTTP server.
        """

        self.server = HTTPServer((host_name, port_number), _MyHandler)
        self.thread = threading.Thread(
            target=self._server_handler, args=(self.server,))

    def start(self):
        """Starts the server"""

        self.thread.start()

    def stop(self):
        """Stops the server"""

        self.server.shutdown()
        self.thread.join()

    def _server_handler(self, server):
        try:
            server.serve_forever()
        except:
            server.server_close()
            raise Exception("Error occurred, server closed")
