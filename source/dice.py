"""Roll Dice!"""


import re
import math
import operator
from random import randint


def _parse_dice(dice_input: str) -> dict:
    """Extract information from a dice-string input."""
    patterns = {
        'count': '\\d*d',
        'sides': 'd\\d*',
        'exploding': 'e\\d*',
        'advantage': '\\+',
        'disadvantage': '\\-',
        'concatenate': 'c',
    }
    re_funcs = {}
    for target, pattern in patterns.items():
        re_funcs[target] = re.compile(pattern).findall

    search_results = {}
    for target, func in re_funcs.items():
        search_results[target] = func(dice_input)

    dice_ = {
        "count": 0,
        "sides": 0,
        "exploding": math.inf,
        "advantage": 0,
        "concatenate": False,
    }
    return dice_



def _validate():
    pass


def _validate_required(substring: list) -> None:
    if len(substring) != 1:
        raise ValueError(f"substring must have length 1: {substring =}")


def _validate_optional(substring: list) -> bool:
    if len(substring) > 0:
        return True
    else:
        return False


def _extract_int(substring: str) -> int:
    """Extracts all numerical characters, in the order they appear, then
    concatenates and runs the int() function."""
    regex = re.compile("\\d")
    search = regex.findall(substring)
    numerals = int("".join(search))
    return numerals


# Advantage/disadvantage default implementation == if you have n adv/dis then you roll
# n more dice of the same type, and keep the highest/lowest n.
