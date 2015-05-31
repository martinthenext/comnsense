import unittest
import pytest
import random

import comnsense_agent.message as M


class MessageTest(unittest.TestCase):
    def test_seq(self):
        ident = random.randint(0, 100)
        kind = random.choice([M.KIND_REQUEST, M.KIND_EVENT, M.KIND_ACTION])
        payload = random.randint(0, 100)
        msg = M.Message(ident, kind, payload)

        def get_seq(*args):
            return args

        msg_parts = get_seq(*msg)
        self.assertEquals(msg_parts[0], ident)
        self.assertEquals(msg_parts[1], kind)
        self.assertEquals(msg_parts[2], payload)

        self.assertEquals(len(msg), 3)
        self.assertEquals(msg.head(), ident)
        self.assertEquals(msg.last(), payload)

    def test_conditions(self):
        for kind in [M.KIND_ACTION, M.KIND_EVENT, M.KIND_REQUEST]:
            ident = random.randint(0, 100)
            payload = random.randint(0, 100)
            msg = M.Message(ident, kind, payload)
            self.assertTrue(getattr(msg, "is_%s" % kind)())
            self.assertEquals(msg.kind, kind)
            self.assertEquals(msg.ident, ident)
            self.assertEquals(msg.payload, payload)
