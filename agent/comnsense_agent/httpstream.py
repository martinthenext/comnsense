import logging
import json
import os

import tornado
import tornado.web
import tornado.httpclient

from comnsense_agent.data import Request, Response
from comnsense_agent.message import Message, MESSAGE_RESPONSE

logger = logging.getLogger(__name__)


class LocalFileStream:
    def __init__(self, server_str, loop, api="v1"):
        self.basepath = os.path.expanduser(os.path.join("~", "comnsense", api))
        self.loop = loop
        self.callback = None
        if not os.path.isdir(self.basepath):
            os.makedirs(self.basepath)

    def on_recv(self, callback=None):
        if callback is None:
            callback = lambda *args: pass
        self.callback = callback

    def send_multipart(self, message):
        try:
            self._send_multipart(message)
        except Exception, e:
            logger.exception(e)

    def _send_multipart(self, message):
        req = Request.deserialize(message.payload)
        if req.type == Request.Type.GetContext:
            context = self.get_context(req.data)
            if context:
                self.callback(
                    message.ident, MESSAGE_RESPONSE,
                    Response.ok(context).serialize())
            else:
                self.callback(
                    message.ident, MESSAGE_RESPONSE,
                    Response.nocontent().serialize())
        elif req.type == Request.Type.SaveContext:
            context = req.data
            self.callback(
                message.ident, MESSAGE_RESPONSE,
                Response.accepted().serialize())
            self.save_context(workbook, context)
            self.callback(
                message.ident, MESSAGE_RESPONSE,
                Response.created().serialize())

    def get_context(self, workbook):
        filename = os.path.join(self.basepath, workbook)
        if os.path.exists(filename, "rb"):
            with open(filename) as h:
                return h.read()

    def save_context(self, workbook, context):
        filename = os.path.join(self.basepath, workbook)
        tmp_filename = os.path.join(self.basepath, workbook + ".tmp")
        with open(tmp_filename, "wb") as h:
            h.write(context)
        os.rename(tmp_filename, filename)


ServerStream = LocalFileStream
