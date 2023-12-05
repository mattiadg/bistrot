import argparse
import importlib
import inspect
import os
import sys
from dataclasses import dataclass, field
from typing import Sequence, Callable

import bistrot


@dataclass(frozen=True)
class Function:
    module: str = field(init=False)
    name: str = field(init=False)
    arguments: inspect.Signature = field(init=False)
    f: Callable

    def __post_init__(self):
        object.__setattr__(self, "module", self.f.__module__)
        object.__setattr__(self, "name", self.f.__name__)
        object.__setattr__(self, "arguments", inspect.signature(self.f))


class FunctionNotFound(Exception):
    pass


class ClassNotFound(Exception):
    pass


def bistrot_exec(name: str, args: Sequence[str]):
    module_name, func_name = name.split(":")
    m = importlib_with_error_message(module_name)
    func = get_function_with_error_message(m, func_name)
    if callable(func):
        f = Function(f=func)
        parser = make_argparser(f)
        args, remaining = parser.parse_known_args(args)
        if remaining:
            parser.print_help()
            parser.error(f"Unrecognized arguments {list(remaining)}")
        return f.f(**vars(args))
    else:  # Not a callable, it is a constant value
        return func


def importlib_with_error_message(module_name: str):
    try:
        m = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        path = module_name.split(".")
        m_name = path[-1]
        if len(path) > 1:
            m_parent = importlib_with_error_message(".".join(path[:-1]))
            err_msg = f" There is no module called {m_name} in {m_parent.__name__}"
        else:
            err_msg = f" There is no module called {m_name}"
        raise ModuleNotFoundError(err_msg) from e
    return m


def get_function_with_error_message(module, func_name: str) -> Callable:
    if "." not in func_name:
        try:
            func = getattr(module, func_name)
        except AttributeError as e:
            raise FunctionNotFound(
                f" There is no function called {func_name} in module {module.__name__}"
            ) from e
    else:
        klass_name, f_name = func_name.split(".")
        try:
            klass = getattr(module, klass_name)
        except AttributeError as e:
            raise ClassNotFound(
                f" There is no class called {klass_name} in module {module.__name__}"
            ) from e
        try:
            func = getattr(klass, f_name)
        except AttributeError as e:
            raise FunctionNotFound(
                f" There is no function called {f_name} in class {klass_name} in module {module.__name__}"
            ) from e

    return func


def make_argparser(func: Function):
    parser = argparse.ArgumentParser(func.name)
    for arg_name, par in func.arguments.parameters.items():
        parser.add_argument(
            f"--{arg_name}", type=par.annotation, help=f"type: {par.annotation}"
        )
    return parser


def prompt_print(s: str):
    print(f"bistrot> {s}")


def main():
    sys.path.append(os.getcwd())
    if "--version" or "-v" in sys.argv:
        prompt_print(bistrot.version)
    else:
        prompt_print(bistrot_exec(sys.argv[1], sys.argv[2:]))


if __name__ == "__main__":
    sys.exit(main())
