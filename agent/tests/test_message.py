import unittest
import pytest
import random
import string
import mock

from comnsense_agent.message import Message, InvalidMessageError
from comnsense_agent.message import MESSAGE_EVENT, MESSAGE_ACTION
from comnsense_agent.message import MESSAGE_REQUEST, MESSAGE_RESPONSE
from comnsense_agent.message import MESSAGE_LOG, MESSAGE_SIGNAL, MESSAGES


class MessageTest(unittest.TestCase):

    def test_action(self):
        payload = "".join(random.sample(string.ascii_letters, 10))
        ident = "".join(random.sample(string.ascii_letters, 10))
        msg = Message.action(payload, ident)
        self.assertTrue(msg.is_action())
        self.assertEquals(msg.ident, ident)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_ACTION)
        msg = Message.action(payload)
        self.assertTrue(msg.is_action())
        self.assertEquals(msg.ident, Message.NO_IDENT)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_ACTION)

    def test_event(self):
        payload = "".join(random.sample(string.ascii_letters, 10))
        ident = "".join(random.sample(string.ascii_letters, 10))
        msg = Message.event(payload, ident)
        self.assertTrue(msg.is_event())
        self.assertEquals(msg.ident, ident)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_EVENT)
        msg = Message.event(payload)
        self.assertTrue(msg.is_event())
        self.assertEquals(msg.ident, Message.NO_IDENT)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_EVENT)

    def test_request(self):
        payload = "".join(random.sample(string.ascii_letters, 10))
        ident = "".join(random.sample(string.ascii_letters, 10))
        msg = Message.request(payload, ident)
        self.assertTrue(msg.is_request())
        self.assertEquals(msg.ident, ident)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_REQUEST)
        msg = Message.request(payload)
        self.assertTrue(msg.is_request())
        self.assertEquals(msg.ident, Message.NO_IDENT)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_REQUEST)

    def test_response(self):
        payload = "".join(random.sample(string.ascii_letters, 10))
        ident = "".join(random.sample(string.ascii_letters, 10))
        msg = Message.response(payload, ident)
        self.assertTrue(msg.is_response())
        self.assertEquals(msg.ident, ident)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_RESPONSE)
        msg = Message.response(payload)
        self.assertTrue(msg.is_response())
        self.assertEquals(msg.ident, Message.NO_IDENT)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_RESPONSE)

    def test_log(self):
        payload = "".join(random.sample(string.ascii_letters, 10))
        ident = "".join(random.sample(string.ascii_letters, 10))
        msg = Message.log(payload, ident)
        self.assertTrue(msg.is_log())
        self.assertEquals(msg.ident, ident)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_LOG)
        msg = Message.log(payload)
        self.assertTrue(msg.is_log())
        self.assertEquals(msg.ident, Message.NO_IDENT)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_LOG)

    def test_signal(self):
        payload = "".join(random.sample(string.ascii_letters, 10))
        ident = "".join(random.sample(string.ascii_letters, 10))
        msg = Message.signal(payload, ident)
        self.assertTrue(msg.is_signal())
        self.assertEquals(msg.ident, ident)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_SIGNAL)
        msg = Message.signal(payload)
        self.assertTrue(msg.is_signal())
        self.assertEquals(msg.ident, Message.NO_IDENT)
        self.assertEquals(msg.payload, payload)
        self.assertEquals(msg.kind, MESSAGE_SIGNAL)

    def test_seq_without_ident(self):
        kind = random.choice(MESSAGES)
        payload = "".join(random.sample(string.ascii_letters, 10))
        msg = Message(kind, payload)
        self.assertEquals(len(msg), 2)
        self.assertEquals(msg[0], kind)
        self.assertEquals(msg[1], payload)
        self.assertEquals(msg["ident"], Message.NO_IDENT)
        self.assertEquals(msg["kind"], kind)
        self.assertEquals(msg["payload"], payload)
        self.assertEquals(msg[0:2], [kind, payload])
        self.assertEquals(msg.head(), kind)
        self.assertEquals(msg.last(), payload)
        self.assertEquals(list(msg), [kind, payload])

    def test_seq(self):
        payload = "".join(random.sample(string.ascii_letters, 10))
        ident = "".join(random.sample(string.ascii_letters, 10))
        kind = random.choice(MESSAGES)
        msg = Message(ident, kind, payload)
        self.assertEquals(len(msg), 3)
        self.assertEquals(msg[0], ident)
        self.assertEquals(msg[1], kind)
        self.assertEquals(msg[2], payload)
        self.assertEquals(msg["ident"], ident)
        self.assertEquals(msg["kind"], kind)
        self.assertEquals(msg["payload"], payload)
        self.assertEquals(msg[0:3], [ident, kind, payload])
        self.assertEquals(msg.head(), ident)
        self.assertEquals(msg.last(), payload)
        self.assertEquals(list(msg), [ident, kind, payload])

    def test_not_implemented(self):
        payload = "".join(random.sample(string.ascii_letters, 10))
        ident = "".join(random.sample(string.ascii_letters, 10))
        kind = random.choice(MESSAGES)
        msg = Message(ident, kind, payload)
        with pytest.raises(NotImplementedError):
            data = reversed(msg)
        with pytest.raises(NotImplementedError):
            msg.append(123)
        with pytest.raises(NotImplementedError):
            del msg[0]

    def test_serializable(self):
        payload = "".join(random.sample(string.ascii_letters, 10))
        kind = random.choice(MESSAGES)
        ident = "".join(random.sample(string.ascii_letters, 10))

        obj = mock.Mock()
        obj.serialize = mock.Mock()
        obj.serialize.return_value = payload

        msg = Message(ident, kind, obj)
        self.assertEquals(msg.payload, payload)

        msg = Message(kind, obj)
        self.assertEquals(msg.payload, payload)

    def test_validate(self):
        kind = random.choice(MESSAGES) + 100
        ident = "".join(random.sample(string.ascii_letters, 10))
        payload = "".join(random.sample(string.ascii_letters, 10))
        with pytest.raises(InvalidMessageError):
            msg = Message(ident, kind, payload)
        msg = Message(ident, random.choice(MESSAGES), payload)
        with pytest.raises(InvalidMessageError):
            msg["kind"] = kind
