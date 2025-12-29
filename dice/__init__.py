"""
Imports an instance of the Roller class, and some functions to easily access
its methods, without having to init this class inside the program using it.
"""


from copy import deepcopy as deepcopy
import inspect
from typing import Any

from dice.src.dice import Roller as Roller


__ALL__ = ["pool", "sum", "show_settings", "change_settings", "get_roller",
           "help"]


def pool(dice_input: str, **kwargs) -> list[int]:
    """Roll the dice, get the result as a list."""
    return _ROLLER.pool(dice_input, **kwargs)


def sum(dice_input: str, **kwargs) -> int:
    """Roll the dice then add them all together."""
    return _ROLLER.sum(dice_input, **kwargs)


def show_settings() -> None:
    """Show the current Roller settings."""
    display = ""
    for setting, value in _SETTINGS.items():
        display += f"{setting}: "
        if isinstance(value, str):
            display += f"'{value}'\n"
        else:
            display += f"{value}\n"
    print(display, end="")


def change_settings(**kwargs) -> None:
    """Create a new roller instance with the modified settings."""
    global _ROLLER
    for key_word, value in kwargs.items():
        _SETTINGS[key_word] = value

    _ROLLER = Roller(**_SETTINGS)


def get_roller(**kwargs) -> Roller:
    """Put in some settings, and get a roller instance back."""
    settings = deepcopy(_DEFAULT_SETTINGS) | kwargs
    return Roller(**settings)


def help() -> None:
    """Display a message showing how to use the module."""
    display = _ROLLER.__doc__ + "\n"
    display += "The dice roller has the following functions:\n"
    for func_name, help_text in _ALL_HELP_TEXT.items():
        display += f"    - dice.{func_name}(): {help_text}\n"
    print(display)


def _get_default_settings() -> dict[str, Any]:
    """
    Grab the default settings for all keyword arguments for Roller.
    """
    parameters = inspect.signature(Roller).parameters
    settings = {}
    for para in parameters.values():
        settings[para.name] = para.default
    return settings


_DEFAULT_SETTINGS = _get_default_settings()
_SETTINGS = deepcopy(_DEFAULT_SETTINGS)
_ROLLER = Roller()

_ALL_HELP_TEXT = {"sum": "", "pool": ""}  # Making sure pool/sum are inserted first.
for _func_name in __ALL__:
    _ALL_HELP_TEXT[_func_name] = locals()[_func_name].__doc__

