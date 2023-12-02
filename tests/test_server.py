from bistrot.server import app, server, register, Server

import threading
from functools import partial


def func1(a: int, b: int) -> int:
    return a + b


def test_func_in_register():
    server(func1)
    assert "tests.test_server:func1" in register


def test_get_server():
    server(func1)
    assert isinstance(register["tests.test_server:func1"], Server)


def test_register_server():
    server(func1)
    ser = register["tests.test_server:func1"]
    t = threading.Thread(target=app.run, kwargs={"host": ser.config.host, "port": ser.config.port})
    t.start()
    t.join()
    assert register["tests.test_server:func1"]