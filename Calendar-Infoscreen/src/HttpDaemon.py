# -*- coding: utf-8 -*-
import logging
import requests

from threading import Thread
from http.server import HTTPServer, SimpleHTTPRequestHandler

logger = logging.getLogger('infoscreen')

class HttpDaemon(Thread):

    stopped = False
    allow_reuse_address = True

    def __init__(self, port=8080, parent=None):
        Thread.__init__(self)
        self.port = port

    def run(self):
        logger.debug("HTTP Server Starting Up")
        self.stopped = False
        try:
            self._server = HTTPServer(('0.0.0.0', int(self.port)), SimpleHTTPRequestHandler)
        except OSError:
            logger.debug("Could not start the server. Perhaps the port is in use. Exiting.")
            return
        self.serve_forever()

    def serve_forever(self):
        logger.debug("Serving over HTTP")
        while not self.stopped:
            self._server.handle_request() #blocks
        logger.debug("HTTP Server Exiting")

    def force_stop(self):
        logger.debug("Requesting HTTP Server Shutdown")
        self.stopped = True
        self.create_dummy_request()
        self.stop()

    def set_port(self, port):
        self.port = port

    def create_dummy_request(self):
        try:
            requests.get("http://%s:%s/web/" % ('127.0.0.1', int(self.port)), timeout=1)
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            pass

    def stop(self):
        self._server.server_close()
