import pytest
import unittest
import string
import random
import tempfile
import os
import shutil
import mock

from comnsense_agent.serverstream import LocalFileStream
from comnsense_agent.data import Response, Request
from comnsense_agent.message import Message


class TestLocalFileStream(unittest.TestCase):
    def setUp(self):
        server_url = "https://comnsense.io"
        self.tmpdir = tempfile.mkdtemp()
        self.stream = LocalFileStream(server_url, None)
        self.stream.basepath = self.tmpdir

    def test_new_context(self):
        workbook = "".join(random.sample(string.ascii_letters, 10))
        ident = "".join(random.sample(string.ascii_letters, 10))
        req = Request.getcontext(workbook)
        msg = Message.request(req, ident)
        callback = mock.Mock()
        self.stream.on_recv(callback)
        self.stream.send_multipart(msg)
        self.assertEquals(len(callback.mock_calls), 1)
        kall = callback.mock_calls[0]
        args = kall[1]
        self.assertEquals(len(args), 3)
        res = Message(*args)
        self.assertEquals(res.ident, ident)
        self.assertTrue(res.is_response())
        res = Response.deserialize(res.payload)
        self.assertEquals(res.code, 404)
        self.assertEquals(res.data, None)

    def tearDown(self):
        if os.path.isdir(self.tmpdir):
            shutil.rmtree(self.tmpdir)
