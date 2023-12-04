# Bistrot
A cli tool that transforms any Python function into an executable

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

It takes an existing Python function in a project and allows you to call it as an independent executable. All the
 function arguments become cli arguments with argparse.

## Examples
Let's consider this example from [examples/ops.py](examples/ops.py): 
```python
#examples/ops.py
def add(a: int, b: int) -> int:
    return a + b
```
We can call this function from the command line using **bistrot**:

```bash
$ bistrot examples.ops:add --x=2 --y=3
5
```

It also works with static and class methods
```python
#examples/klass.py
import bistrot

class UsefulClass:
    @staticmethod
    def version():
        return bistrot.__version__
```

```bash
$ bistrot examples.klass:UsefulClass.version
0.1.0
```


## Warning
This project is still experimental and is guaranteed to work only with primitive Python types.