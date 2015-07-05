#!/usr/bin/env python2
import argparse
import uuid
import zmq
import threading
import random
import string


try:
    import comnsense_agent
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import comnsense_agent

from comnsense_agent.data import Event, Cell
from comnsense_agent.message import Message


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--agent", type=str,
                        help="agent connection",
                        default="tcp://127.0.0.1:8888")
    parser.add_argument("-i", "--ident", type=str,
                        default=str(uuid.uuid1()))
    return parser.parse_args()


def get_random_cell():
    key = "$%s$%d" % (random.choice(string.ascii_uppercase),
                      random.choice(range(10)))
    value = random.choice(string.ascii_letters)
    return Cell(key, value)


def loop(ctx, ident, agent, publ):
    socket = ctx.socket(zmq.DEALER)
    socket.setsockopt(zmq.IDENTITY, ident)
    socket.connect(agent)

    subscr = ctx.socket(zmq.REQ)
    subscr.connect(publ)

    subscr.send_multipart(["OK"])

    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    poller.register(subscr, zmq.POLLIN)

    sheet = "sheet"

    working = True
    while working:
        socks = dict(poller.poll())
        if socket in socks and socks[socket] == zmq.POLLIN:
            print socket.recv_multipart()
        if subscr in socks and socks[subscr] == zmq.POLLIN:
            message = subscr.recv_multipart()
            print "from main", message
            cmd = message[0].upper()
            args = message[1:]
            if cmd == "END":
                working = False
            elif cmd == "CHANGE":
                event = Event(Event.Type.SheetChange, ident, sheet,
                              [[get_random_cell()]], [[get_random_cell()]])
                msg = Message.event(event)
                socket.send_multipart(list(msg))
                subscr.send_multipart(["OK"])
            elif cmd == "OPEN":
                event = Event(Event.Type.WorkbookOpen, ident, sheet)
                msg = Message.event(event)
                socket.send_multipart(list(msg))
                subscr.send_multipart(["OK"])


def main(args):
    ctx = zmq.Context()

    publsh = ctx.socket(zmq.REP)
    publsh_str = "inproc://cmdloop"
    publsh.bind(publsh_str)

    cmdloop = threading.Thread(
        target=loop, args=(ctx, args.ident, args.agent, publsh_str))
    cmdloop.start()

    while True:
        answer = publsh.recv_multipart()
        print "from loop", answer
        cmdline = raw_input(">>: ")
        publsh.send_multipart(cmdline.split(" "))
        if cmdline == "END":
            break

    cmdloop.join()

if __name__ == '__main__':
    args = parse_args()
    main(args)
