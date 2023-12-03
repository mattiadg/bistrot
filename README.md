# Bistrot
A cli tool that transforms any Python function into an executable


It takes an existing Python function in a project and allows you to call it as an independent executable. All the
 function arguments become cli arguments with argparse.

## Example
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

## Warning
This project is still experimental and is guaranteed to work only with primitive Python types.