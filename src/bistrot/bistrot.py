import argparse
import importlib
import inspect
import os
import sys
from dataclasses import dataclass, field
from textwrap import dedent
from typing import Sequence, Callable, Any


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


class ParsingError(Exception):
    pass


def bistrot_exec(name: str, args: Sequence[str]):
    try:
        module_name, func_name = name.split(":")
    except ValueError as err:
        raise ParsingError(
            "Missing colon (:) to separate module and function!"
        ) from err
    if "{" in module_name and "}" not in module_name:
        raise ParsingError('Found "{" but missing "}"')
    if "{" in module_name and not module_name.startswith("{"):
        raise ParsingError('Symbol "{" must start a command if present')
    if "}" in module_name and not module_name.endswith("}"):
        raise ParsingError('Symbol "}" must end a module name if present')
    if "{" in module_name:
        return exec_value_function(module_name[1:-1], func_name, args)
    return exec_module_func(module_name, func_name, args)


def exec_module_func(module_name: str, func_name: str, args: Sequence[str]) -> Any:
    m = importlib_with_error_message(module_name)
    func = get_function_with_error_message(m, func_name)
    if callable(func):
        return exec_func(func, args)
    else:  # Not a callable, it is a constant value
        return func


def exec_value_function(value_name: str, func_name: str, args: Sequence[str]) -> Any:
    if value_name.startswith('"') and value_name.endswith('"'):
        method = getattr(value_name[1:-1], func_name)
        return exec_func(method, args)


def exec_func(func, args):
    f = Function(f=func)
    parser = make_argparser(f)
    args = parser.parse_args(args)
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


class PosOrOptAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest) is None:
            setattr(namespace, self.dest, values)


def make_argparser(func: Function):
    parser = argparse.ArgumentParser(func.name)
    for arg_name, par in func.arguments.parameters.items():
        kwargs = {"type": par.annotation, "help": f"type: {par.annotation}"}
        if par.kind == inspect.Parameter.POSITIONAL_ONLY:
            parser.add_argument(arg_name, **kwargs)
        elif par.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            parser.add_argument(arg_name, action=PosOrOptAction, nargs="?", **kwargs)
            kwargs["help"] = (
                kwargs["help"] + f"\nSame as positional argument {arg_name}"
            )
            parser.add_argument(f"--{arg_name}", action=PosOrOptAction, **kwargs)
        elif par.kind == inspect.Parameter.KEYWORD_ONLY:
            parser.add_argument(f"--{arg_name}", **kwargs)
        else:
            print(f"There are additional arguments: {arg_name}")
    return parser


def prompt_print(s: str):
    print(f"bistrot> {s}")


def cli_parser() -> argparse.ArgumentParser:
    from bistrot.__about__ import version

    parser = argparse.ArgumentParser(
        "bistrot - Cook your Python programs and serve them back to you"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"bistrot -- v{version}",
        help="Print software version",
    )
    parser.add_argument(
        "cmd",
        help=dedent(
            """\
            Command to execute.
            It must be in one of the following formats:
            "path.to.module:foo"  --- executes "foo" inside module |
            {"astring"}:foo --- executes method foo for string "astring" |
            "path.to.module:Class.foo" --- executes static or class method "foo" of class "Class" 
            """
        ),
    )
    return parser


def main():
    sys.path.append(os.getcwd())
    parser = cli_parser()
    known_args, rest = parser.parse_known_args(sys.argv[1:])
    prompt_print(bistrot_exec(known_args.cmd, rest))


if __name__ == "__main__":
    sys.exit(main())
