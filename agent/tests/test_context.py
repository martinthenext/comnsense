import pytest
import unittest
import random
import string
import mock

from comnsense_agent.context import Context
from .common import get_random_workbook_id, get_random_sheet_name
from .common import get_random_cell


class TestContext(unittest.TestCase):
    def test_workbook_id(self):
        workbook_id = get_random_workbook_id()
        context = Context()
        context.workbook = workbook_id
        self.assertEquals(context.workbook, workbook_id)

    def test_serialization(self):
        workbook_id = get_random_workbook_id()
        one = Context()
        one.workbook = workbook_id
        another = Context()
        another.workbook = workbook_id
        data = one.dumps()
        another.loads(data)
        self.assertEquals(one, another)
