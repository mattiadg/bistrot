import functools
import inspect
from typing import Callable
from dataclasses import dataclass, field
import logging

from flask import Flask, json, request


app = Flask(__name__)


@dataclass(frozen=True)
class FunctionServer:
    module: str
    name: str
    arguments: inspect.Signature
    f: Callable


@dataclass(frozen=True)
class ServerConfig:
    function: FunctionServer
    host: str
    port: int

    def url(self):
        return f"{self.host}:{self.port}/{self.function.name}"

    def health(self):
        return f"{self.url()}/health"


@dataclass
class Server:
    config: ServerConfig

    def run(self):
        logging.info("run")
        input = json.loads(request.data)
        logging.info(f"Calling {self.config.function.f}({input})")
        output = self.config.function.f(**input)
        return {"result": output}



@dataclass
class Register:
    servers: dict[str, Server] = field(default_factory=dict)

    def register(self, func: Callable):
        """
        Register a server by name
        :param func:
        :return:
        """
        keyname = self.make_name(func)
        if keyname in self.servers:
            return
        funSer = FunctionServer(module=keyname, name=func.__name__, arguments=inspect.signature(func), f=func)
        config = ServerConfig(function=funSer, host="localhost", port=4000)
        ser = Server(config)
        make_route(ser)
        self.servers[keyname] = ser

    def __contains__(self, item):
        return self.servers.__contains__(item)

    def __getitem__(self, item) -> Server:
        return self.servers.__getitem__(item)

    @staticmethod
    def make_name(func: Callable) -> str:
        return f"{func.__module__}:{func.__name__}"


def make_route(ser: Server):
    app.post(f"/{ser.config.function.name}")(ser.run)


register = Register()


def server(func):
    @functools.wraps
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    register.register(func)
    return wrapper
