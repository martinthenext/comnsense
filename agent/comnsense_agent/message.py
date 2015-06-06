import logging

logger = logging.getLogger(__name__)

MESSAGE_EVENT = "event"
MESSAGE_ACTION = "action"
MESSAGE_REQUEST = "req"
MESSAGE_RESPONSE = "res"
MESSAGE_LOG = "log"
MESSAGE_SIGNAL = "sig"

MESSAGES = [
    MESSAGE_EVENT,
    MESSAGE_ACTION,
    MESSAGE_REQUEST,
    MESSAGE_RESPONSE,
    MESSAGE_LOG,
    MESSAGE_SIGNAL
]


class InvalidMessageError(RuntimeError):
    pass


class Message:
    NO_IDENT = 0
    __slots__ = ("ident", "kind", "payload")

    def __init__(self, *message):
        if len(message) == 2:
            message = (Message.NO_IDENT, message[0], message[1])
        if hasattr(message[2], "serialize"):
            message = (message[0], message[1], message[2].serialize())
        for name, value in zip(self.__slots__, message):
            setattr(self, name, value)
        self.validate()

    def validate(self):
        if self.kind not in MESSAGES:
            raise InvalidMessageError(
                "unknown message kind: %s" % self.kind)
        # TODO validate ident here

    def __len__(self):
        if self.ident == Message.NO_IDENT:
            return len(self.__slots__) - 1
        return len(self.__slots__)

    def __getitem__(self, key):
        shift = 0
        if self.ident == Message.NO_IDENT:
            shift = 1
        if isinstance(key, slice):
            return [getattr(self, x) for x in
                    self.__slots__[key.start + shift: key.stop + shift]]
        if isinstance(key, int):
            key = self.__slots__[key + shift]
        if key not in self.__slots__:
            raise KeyError("unknown part: %s" % key)
        return getattr(self, key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = self.__slots__[key]
        if key not in self.__slots__:
            raise KeyError("unknown part: %s" % key)
        setattr(self, key, value)
        self.validate()

    def __delitem__(self, key):
        raise NotImplementedError("could not delete key: %s", key)

    def __iter__(self):
        shift = 0
        if self.ident == Message.NO_IDENT:
            shift = 1
        return (getattr(self, x) for x in self.__slots__[shift:])

    def __reversed__(self):
        raise NotImplementedError("could not reverse message")

    def __str__(self):
        if self.ident == Message.NO_IDENT:
            return "MSG {kind: %s, payload: %r}" % (self.kind, self.payload)
        return "MSG { ident:%r, kind:%s, payload:%r }" % (
            self.ident, self.kind, self.payload)

    def append(self, value):
        raise NotImplementedError("could not append to message")

    def head(self):
        if self.ident == Message.NO_IDENT:
            return self.kind
        return self.ident

    def last(self):
        return self.payload

    def is_action(self):
        return self.kind == MESSAGE_ACTION

    @staticmethod
    def action(payload, ident=None):
        return Message(ident or Message.NO_IDENT, MESSAGE_ACTION, payload)

    def is_event(self):
        return self.kind == MESSAGE_EVENT

    @staticmethod
    def event(payload, ident=None):
        return Message(ident or Message.NO_IDENT, MESSAGE_EVENT, payload)

    def is_request(self):
        return self.kind == MESSAGE_REQUEST

    @staticmethod
    def request(payload, ident=None):
        return Message(ident or Message.NO_IDENT, MESSAGE_REQUEST, payload)

    def is_response(self):
        return self.kind == MESSAGE_RESPONSE

    @staticmethod
    def response(payload, ident=None):
        return Message(ident or Message.NO_IDENT, MESSAGE_RESPONSE, payload)

    def is_log(self):
        return self.kind == MESSAGE_LOG

    @staticmethod
    def log(payload, ident=None):
        return Message(ident or Message.NO_IDENT, MESSAGE_LOG, payload)

    def is_signal(self):
        return self.kind == MESSAGE_SIGNAL

    @staticmethod
    def signal(payload, ident=None):
        return Message(ident or Message.NO_IDENT, MESSAGE_SIGNAL, payload)

    @staticmethod
    def call(callback, log=None):
        if log is None:
            log = logger

        def oncall(message):
            try:
                msg = Message(*message)
                return callback(msg)
            except InvalidMessageError, e:
                log.warn(e)
            except Exception, e:
                log.exception(e)
        return oncall
