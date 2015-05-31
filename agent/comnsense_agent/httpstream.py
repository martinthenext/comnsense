import logging
import json

import tornado
import tornado.web
import tornado.httpclient

logger = logging.getLogger(__name__)


class HTTPStream:
    IDENT_HEADER = 'X-Ident'
    USER_AGENT = "ComnsenseAgent"

    def __init__(self, server_str, loop, api="v1"):
        self.baseurl = "%s/%s/%%s" % (server_str, api)
        logger.debug("baseurl: %s", self.baseurl)
        self.client = tornado.httpclient.AsyncHTTPClient()
        self.callback = None

    def on_recv(self, callback=None):
        self.callback = callback

    def on_recv_callback(self, response):
        code = response.code
        body = response.body
        ident = response.headers.get(self.IDENT_HEADER)
        logger.debug(
            "receiving response with code %d and ident %s", code, ident)
        logger.debug("  with body:\n%s", body)
        if self.callback:
            self.callback(ident or "", code, body)

    @tornado.web.asynchronous
    def send(self, *messages):
        ident, _, call, _, payload = messages
        url = self.baseurl % call
        headers = {}
        if ident:
            headers[self.IDENT_HEADER] = ident
        logger.debug("sending request to url: %s", url)
        logger.debug("  with body:\n%s", payload)
        self.client.fetch(url, method="POST", body=payload,
                          user_agent=self.USER_AGENT,
                          callback=self.on_recv_callback,
                          raise_error=False)
