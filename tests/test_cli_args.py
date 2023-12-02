from bistrot.cli_args import make_parser
from bistrot.server import register, server


def func1(a: int, b: int) -> int:
    return a + b


def test_make_parser_good():
    server(func1)
    parser = make_parser(register, func1)
    args = parser.parse_args(["--a", "1", "--b", "2"])
    assert args.a == 1
    assert args.b == 2
