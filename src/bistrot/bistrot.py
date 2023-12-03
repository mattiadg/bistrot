import argparse
import importlib
import inspect
import sys
from dataclasses import dataclass, field
from typing import Sequence, Callable


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


def bistrot_exec(name: str, args: Sequence[str]):
    module_name, func_name = name.split(":")
    m = importlib_with_error_message(module_name)
    func = get_function_with_error_message(m, func_name)
    f = Function(f=func)
    parser = make_parser(f)
    args, remaining = parser.parse_known_args(args)
    if remaining:
        parser.print_help()
        parser.error(f"Unrecognized arguments {list(remaining)}")
    return f.f(**vars(args))


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


def get_function_with_error_message(module, func_name: str) ->  Callable:
    try:
        func = getattr(module, func_name)
    except AttributeError as e:
        raise AttributeError(f" There is no function called {func_name} in module {module.__name__}") from e
    return func


def make_parser(func: Callable):
    parser = argparse.ArgumentParser(func.name)
    for arg_name, par in func.arguments.parameters.items():
        parser.add_argument(f"--{arg_name}", type=par.annotation, help=f"type: {par.annotation}")
    return parser


def main():
    print(bistrot_exec(sys.argv[1], sys.argv[2:]))


if __name__ == '__main__':
    sys.exit(main())
