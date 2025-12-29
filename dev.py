"""
Contains functions intended primarily to be used in interactive mode.
"""


import rich


__ALL__ = ["doc", "inspect"]


def doc(obj) -> None:
    """Print an object's documentation."""
    print(obj.__doc__)


def inspect(obj) -> None:
    """Use Rich's inspect function."""
    rich.inspect(obj)
