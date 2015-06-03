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
                "format": "%(asctime)s: %(levelname)s: %(ident)s: %(name)s: %(message)s",
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
        config["handlers"]["syslog"] = {
            "class": "logging.handlers.NTEventLogHandler",
            "formatter": "syslog",
            "appname": "Comnsense Agent",
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


def worker_setup(socket, ident):
    config = {
        "version": 1,
        "handlers": {
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
            "level": "DEBUG",
        },
        "loggers": {
            "comnsense_agent": {},
            "tornado": {},
        }
    }
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
            data = pickle.dumps(record)
            self.socket.send_multipart(M.message(data))
        except:
            self.handleError(record)
