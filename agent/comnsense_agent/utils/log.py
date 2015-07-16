import logging
import logging.config
import os
import platform
import pickle

from comnsense_agent.message import Message


class IdentFilter(logging.Filter):
    def __init__(self, ident=None):
        self.ident = ident

    def filter(self, record):
        if not hasattr(record, "ident"):
            record.ident = self.ident
        return True


def setup(level, filename=None):
    config = {
        "version": 1,
        "handlers": {
        },
        "formatters": {
            "file": {
                "format": ("%(asctime)s: %(levelname)s: "
                           "%(ident)s: %(name)s: %(message)s"),
            },
            "syslog": {
                "format": "comnsense-agent: %(ident)s: %(name)s: %(message)s",
            },
        },
        "filters": {
            "ident": {
                "()": IdentFilter,
                "ident": "main",
            },
        },
        "root": {
            "handlers": ["syslog"],
            "level": level,
        },
        "loggers": {
            "comnsense_agent": {},
            "tornado": {},
        }
    }
    if filename is not None:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "file",
            "filename": filename,
            "maxBytes": 1000000,
            "backupCount": 5,
            "filters": ["ident"],
        }
        config["root"]["handlers"].append("file")
    if platform.system().lower() == "windows":
        appdata = os.getenv('APPDATA')
        if appdata and os.path.isdir(appdata):
            if not os.path.isdir(os.path.join(appdata, "Comnsense")):
                os.makedirs(os.path.join(appdata, "Comnsense"))
            filename = os.path.join(appdata, "Comnsense", "Agent.log")
            config["handlers"]["syslog"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "file",
                "filename": filename,
                "maxBytes": 1000000,
                "backupCount": 50,
                "filters": ["ident"],
            }
    elif platform.system().lower() == "darwin":
        config["handlers"]["syslog"] = {
            "class": "logging.handlers.SysLogHandler",
            "formatter": "syslog",
            "facility": "daemon",
            "address": "/var/run/syslog",
            "filters": ["ident"],
        }
    else:
        config["handlers"]["syslog"] = {
            "class": "logging.handlers.SysLogHandler",
            "formatter": "syslog",
            "facility": "daemon",
            "address": "/dev/log",
            "filters": ["ident"],
        }
    logging.config.dictConfig(config)


def worker_setup(socket, ident, level=None):
    if level is None:
        level = "DEBUG"
    config = {
        "version": 1,
        "handlers": {
            "stream": {
                "class": "logging.StreamHandler",
            },
            "zmq": {
                "class": "comnsense_agent.utils.log.ZLogHandler",
                "socket": socket,
                "filters": ["ident"],
            },
        },
        "filters": {
            "ident": {
                "()": IdentFilter,
                "ident": ident,
            },
        },
        "root": {
            "handlers": ["zmq"],
            "level": level,
        },
        "loggers": {
            "comnsense_agent": {},
            "tornado": {},
        }
    }
    if level == "DEBUG":
        config["root"]["handlers"].append("stream")
    logging.config.dictConfig(config)


class ZLogHandler(logging.Handler):
    def __init__(self, socket, level=logging.NOTSET):
        self.socket = socket
        super(ZLogHandler, self).__init__()

    def emit(self, record):
        try:
            if record.exc_info:
                dummy = self.format(record)
                record.exc_info = None
            data = None
            try:
                data = pickle.dumps(record)
            except TypeError:
                self.format(record)
                data = pickle.dumps(record)
            self.socket.send_multipart(list(Message.log(data)))
        except:
            self.handleError(record)
