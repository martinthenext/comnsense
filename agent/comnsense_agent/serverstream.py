import logging
import os

from comnsense_agent.data import Request, Response
from comnsense_agent.message import Message, MESSAGE_RESPONSE

logger = logging.getLogger(__name__)


class LocalFileStream(object):
    def __init__(self, server_str, loop, api="v1"):
        self.basepath = os.path.expanduser(os.path.join("~", "comnsense", api))
        self.loop = loop
        self.callback = self.default_callback

    def default_callback(self):
        pass

    def on_recv(self, callback=None):
        if callback is None:
            callback = self.default_callback
        self.callback = callback

    def send(self, message):
        try:
            if not os.path.isdir(self.basepath):
                os.makedirs(self.basepath)
            self._send_multipart(message)
        except Exception, e:
            logger.exception(e)
            raise

    def _send_multipart(self, message):
        req = Request.deserialize(message.payload)
        if req.type == Request.Type.GetContext:
            context = self.get_context(req.data["workbook"])
            if context:
                self.callback(Message.response(Response.ok(context),
                                               message.ident))
            else:
                self.callback(Message.response(Response.notfound(),
                                               message.ident))
        elif req.type == Request.Type.SaveContext:
            context = req.data
            self.callback(Message.response(Request.accepted(),
                                           message.ident))
            self.save_context(context["workbook"], context)
            self.callback(Message.response(Request.created(),
                                           message.ident))

    def get_context(self, workbook):
        filename = os.path.join(self.basepath, workbook)
        if os.path.exists(filename):
            with open(filename, "rb") as h:
                return h.read()

    def save_context(self, workbook, context):
        filename = os.path.join(self.basepath, workbook)
        tmp_filename = os.path.join(self.basepath, workbook + ".tmp")
        with open(tmp_filename, "wb") as h:
            h.write(context)
        os.rename(tmp_filename, filename)


ServerStream = LocalFileStream
