"""
Imports an instance of the Roller class, and some functions to easily access
its methods, without having to init this class inside the program using it.
"""


# help() assumes any non-public function has _ in front of it.
from copy import deepcopy as _deepcopy
from dice.src.dice import Roller as _Roller


_ROLLER = _Roller()
_DEFAULT_SETTINGS = {
    "randint_method": "builtin-randint",
    "advantage_method": "add-dice",
    "roll_method": "roll-over",
}
_SETTINGS = _deepcopy(_DEFAULT_SETTINGS)


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
        display += f"{setting}: {value}\n"
    print(display)


def change_settings(**kwargs) -> None:
    """Create a new roller instance with the modified settings."""
    global _ROLLER
    for key_word, value in kwargs.items():
        _SETTINGS[key_word] = value

    _ROLLER = _Roller(**_SETTINGS)


def _is_public_name(name: str) -> bool:
    """
    Determines if a name is public.
    """
    if name[0] == "_" or name == "src":
        return False
    else:
        return True


def get_roller(**kwargs) -> _Roller:
    """Put in some settings, and get a roller instance back."""
    settings = _deepcopy(_DEFAULT_SETTINGS) | kwargs
    return _Roller(**settings)


_ALL_FUNCTION_NAMES = filter(_is_public_name, dir())
_ALL_HELP_TEXT = {"sum": "", "pool": ""}  # Making sure pool/sum are inserted first.
for _func_name in _ALL_FUNCTION_NAMES:
    _ALL_HELP_TEXT[_func_name] = locals()[_func_name].__doc__


def help() -> None:
    """Display a message showing how to use the module."""
    display = _ROLLER.__doc__ + "\n"
    display += "The dice roller has the following functions:\n"
    for func_name, help_text in _ALL_HELP_TEXT.items():
        display += f"    - dice.{func_name}(): {help_text}\n"
    print(display)
