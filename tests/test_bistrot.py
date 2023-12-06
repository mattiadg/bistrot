from dataclasses import dataclass

import pytest

from bistrot.bistrot import (
    bistrot_exec,
    make_argparser,
    Function,
    ClassNotFound,
    FunctionNotFound,
    ParsingError,
)


def func1(a: int, b: int) -> int:
    return a + b


def func2(s: str, x: int) -> str:
    return f"{s}+{x}+{s}"


@dataclass
class AClass:
    @staticmethod
    def astaticmethod(x: float) -> float:
        return x**3

    @classmethod
    def aclassmethod(cls, val: str):
        return AClass()


def test_bistrot_exec_ok_int():
    result = bistrot_exec("tests.test_bistrot:func1", ("--a", "1", "--b", "2"))
    assert result == 3


def test_bistrot_exec_ok_str():
    result = bistrot_exec("tests.test_bistrot:func2", ("--s", "ciaociao", "--x", "4"))
    assert result == "ciaociao+4+ciaociao"


def test_bistrot_exec_wrong_func():
    with pytest.raises(FunctionNotFound) as err:
        bistrot_exec("tests.test_bistrot:xxx", ("--s", "ciaociao", "--x", "4"))
    assert "xxx" in str(err)


def test_bistrot_exec_wrong_module():
    with pytest.raises(ModuleNotFoundError) as err:
        bistrot_exec("tests.test_bistt:func1", ("--s", "ciaociao", "--x", "4"))
    assert "test_bistt" in str(err) and "tests" in str(err)


def test_bistrot_exec_wrong_root_module():
    with pytest.raises(ModuleNotFoundError) as err:
        bistrot_exec("wow.test_bistrot:func1", ("--s", "ciaociao", "--x", "4"))
    assert "test_bistrot" not in str(err) and "wow" in str(err)


def test_bistrot_exec_wrong_args():
    with pytest.raises(SystemExit):
        bistrot_exec("tests.test_bistrot:func1", ("--x", "1", "--b", "2"))


def test_bistrot_exec_missing_colon():
    with pytest.raises(ParsingError):
        bistrot_exec("tests.test_bistrot.func1", ("--x", "1", "--b", "2"))


def test_bistrot_exec_static_method_ok():
    result = bistrot_exec("tests.test_bistrot:AClass.astaticmethod", ("--x", "2.0"))
    assert result == 8.0


def test_bistrot_exec_class_method_ok():
    result = bistrot_exec(
        "tests.test_bistrot:AClass.aclassmethod", ("--val", "teststr")
    )
    assert result == AClass()


def test_bistrot_exec_static_method_class_not_found():
    with pytest.raises(ClassNotFound) as err:
        bistrot_exec("tests.test_bistrot:BClass.astaticmethod", ("--x", "2.0"))
    assert "BClass" in str(err)


def test_bistrot_exec_static_method_function_not_found():
    with pytest.raises(FunctionNotFound) as err:
        bistrot_exec("tests.test_bistrot:AClass.bstaticmethod", ("--x", "2.0"))
    assert "bstaticmethod" in str(err)


def test_bistrot_exec_variable():
    from bistrot import __version__

    version = bistrot_exec("bistrot:__version__", ())
    assert __version__ == version


def test_bistrot_exec_value():
    result = bistrot_exec('{"hello"}:upper', ())
    assert result == "HELLO"


def test_bistrot_exec_value_nonclosed_curly():
    with pytest.raises(ParsingError) as err:
        bistrot_exec('{"hello":upper', ())

    assert "missing \"}\"" in str(err)


def test_bistrot_exec_value_wrong_open_curly():
    with pytest.raises(ParsingError):
        bistrot_exec('"he{llo":upper', ())


def test_bistrot_exec_value_wrong_closed_curly():
    with pytest.raises(ParsingError):
        bistrot_exec('"hell}o":upper', ())


def test_make_parser_good():
    f = Function(f=func1)
    parser = make_argparser(f)
    args = parser.parse_args(["--a", "1", "--b", "2"])
    assert args.a == 1
    assert args.b == 2
