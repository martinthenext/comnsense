import pytest
import unittest
import random
import string

from comnsense_agent.data import Request


class TestRequest(unittest.TestCase):
    def test_getcontext(self):
        workbook = "".join(random.sample(string.ascii_letters, 10))
        req = Request.getcontext(workbook)
        self.assertEquals(req.data, {"workbook": workbook})
        self.assertEquals(req.type, Request.Type.GetContext)
        self.assertEquals(req.get_url(), "agent/context/%s" % workbook)
        self.assertEquals(req.get_method(), "GET")
        self.assertEquals(req.get_body(), "")
        data = req.serialize()
        another = Request.deserialize(data)
        self.assertEquals(req.data, another.data)
        self.assertEquals(req.type, another.type)

    def test_savecontext(self):
        workbook = "".join(random.sample(string.ascii_letters, 10))
        context = u"".join(random.sample(string.letters * 100, 1000))
        req = Request.savecontext(workbook, context)
        self.assertEquals(req.data, {"workbook": workbook, "context": context})
        self.assertEquals(req.type, Request.Type.SaveContext)
        self.assertEquals(req.get_url(), "agent/context/%s" % workbook)
        self.assertEquals(req.get_method(), "POST")
        self.assertEquals(req.get_body(), context)
        data = req.serialize()
        another = Request.deserialize(data)
        self.assertEquals(req.data, another.data)
        self.assertEquals(req.type, another.type)
