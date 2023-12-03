import pytest

from src.bistrot.bistrot import bistrot_exec, make_parser, Function


def func1(a: int, b: int) -> int:
    return a + b


def func2(s: str, x: int) -> str:
    return f"{s}+{x}+{s}"


def test_bistrot_exec_ok_int():
    result = bistrot_exec("tests.test_bistrot:func1", ("--a", "1", "--b", "2"))
    assert result == 3


def test_bistrot_exec_ok_str():
    result = bistrot_exec("tests.test_bistrot:func2", ("--s", "ciaociao", "--x", "4"))
    assert result == "ciaociao+4+ciaociao"


def test_bistrot_exec_wrong_func():
    with pytest.raises(AttributeError) as err:
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
    with pytest.raises(SystemExit) as err:
        bistrot_exec("tests.test_bistrot:func1", ("--x", "1", "--b", "2"))


def test_make_parser_good():
    f = Function(f=func1)
    parser = make_parser(f)
    args = parser.parse_args(["--a", "1", "--b", "2"])
    assert args.a == 1
    assert args.b == 2
