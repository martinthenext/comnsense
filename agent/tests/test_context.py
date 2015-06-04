import pytest
import unittest
import random
import string

from comnsense_agent.context import Context


class TestContext(unittest.TestCase):
    def test_workbook_id(self):
        workbook_id = "".join(random.sample(string.ascii_letters, 10))
        context = Context()
        context.workbook = workbook_id
        self.assertEquals(context.workbook, workbook_id)

    def test_serialization(self):
        workbook_id = "".join(random.sample(string.ascii_letters, 10))
        one = Context()
        one.workbook = workbook_id
        another = Context()
        another.workbook = workbook_id
        data = one.dumps()
        another.loads(data)
        self.assertEquals(one, another)
