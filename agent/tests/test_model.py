import pytest
import unittest
import random
import string

from comnsense_agent.model import Model


class TestModel(unittest.TestCase):
    def test_workbook_id(self):
        workbook_id = "".join(random.sample(string.ascii_letters, 10))
        model = Model()
        model.workbook = workbook_id
        self.assertEquals(model.workbook, workbook_id)

    def test_serialization(self):
        workbook_id = "".join(random.sample(string.ascii_letters, 10))
        one = Model()
        one.workbook = workbook_id
        another = Model()
        another.workbook = workbook_id
        data = one.dumps()
        another.loads(data)
        self.assertEquals(one, another)
