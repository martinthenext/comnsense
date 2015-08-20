import pytest
import tornado.ioloop
import zmq.eventloop.ioloop


@pytest.yield_fixture
def io_loop():
    loop = tornado.ioloop.IOLoop()
    loop.make_current()

    yield loop

    loop.clear_current()
    if (not tornado.ioloop.IOLoop.initialized() or
            loop is not tornado.ioloop.IOLoop.instance()):
        loop.close(all_fds=True)


@pytest.yield_fixture
def zmq_io_loop():
    loop = zmq.eventloop.ioloop.IOLoop()
    loop.make_current()

    yield loop

    loop.clear_current()
    if (not tornado.ioloop.IOLoop.initialized() or
            loop is not tornado.ioloop.IOLoop.instance()):
        loop.close(all_fds=True)
