import argparse
from typing import Callable

from .server import Register


def make_parser(register: Register, func: Callable):
    func_key = register.make_name(func)
    server = register[func_key]
    f = server.config.function
    parser = argparse.ArgumentParser(f.name)
    for arg_name, par in f.arguments.parameters.items():
        parser.add_argument(f"--{arg_name}", type=par.annotation)
    return parser
