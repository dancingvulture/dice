"""A Module containing some dice rollers."""


import re
import math
import operator
import random
import numpy as np

class Roller:
    """
    A die roller that can take readable string inputs ('1d20', '3d6', etc.)
    into its rolling methods (sum or pool). It uses the following syntax:
    [N]dS[eX][+][-]
        - Optional parameters are bracketed.
        - [N] Number of dice to roll, if not entered it default to 1.
        - [eX] exploding dice, where X is the number a result must be equal to
          or greater than in order to explode.
        - [+] advantage, one advantage for every + symbol.
        - [-] disadvantage, one disadvantage for every - symbol.
    """
    random_generators = {}
    def __init__(self, randint_method=None, advantage_method=None):
        # PREFERENCES
        random_generators = {
            None: random.randint,       # Default.
            "numpy": np.random.randint  # 5x slower than python's built-in.
        }
        self._randint = random_generators[randint_method]

        advantage_methods = {
            None: "Not implemented",     # Default.
            "double": "Not implemented"  # Roll all n times, take best.
        }
        self._advantage_method = advantage_methods[advantage_method]

        # CONSTANTS
        # Generate the regex functions used to parse dice inputs.
        patterns = {
            "count": "^\\d+",
            "sides": "d\\d*",
            "exploding": "e\\d*",
            "advantage": "\\++",
            "disadvantage": "\\-+",
        }
        self._regex_funcs = {}
        for parameter, pattern in patterns.items():
            self._regex_funcs[parameter] = re.compile(pattern).findall

        # A few hardcoded attributes that will be needed to validate dice inputs.
        self._result_validation_args = {
            "count": ((operator.gt, 1, Exception), (operator.ne, 1, False)),
            "sides": ((operator.ne, 1, Exception),),
            "exploding": ((operator.gt, 1, Exception), (operator.ne, 1, False)),
            "advantage": ((operator.eq, 0, False),),
            "disadvantage": ((operator.eq, 0, False),),
        }

        # Default values for each parameter.
        self._default_values = {
            "count": 1,
            "sides": 0,
            "exploding": math.inf,
            "advantage": 0,
            "disadvantage": 0,
        }

        # Functions used to process regex search results for each parameter.
        self._processing_funcs = {
            "count": lambda x: int(x[0]),
            "sides": lambda x: self._extract_int(x[0]),
            "exploding": lambda x: self._extract_int(x[0]),
            "advantage": lambda x: len(x),
            "disadvantage": lambda x: len(x),
        }

    def pool(self, dice_input: str) -> list[int]:
        """
        Roll the dice, get the result as a list.
        """
        dice = self._parse_dice(dice_input)
        return self._roll(*dice.values())

    def sum(self, dice_input: str) -> int:
        """
        Roll the dice, then add them all together.
        """
        dice = self._parse_dice(dice_input)
        return sum(self._roll(*dice.values()))

    def _roll(self, count: int, sides: int, exploding: int | float,
              advantage: int, disadvantage: int) -> list[int]:
        pass

    def _parse_dice(self, dice_input: str) -> dict:
        """
        Extract information from a dice-string input.
        """
        # First we do a regex search for each parameter.
        search_results = {}
        for parameter, findall in self._regex_funcs.items():
            search_results[parameter] = findall(dice_input.casefold())

        # Then we validate each search result, making sure the user
        # input wasn't malformed, and telling us which optional arguments
        # they used.
        validation_results = {}
        for parameter, result in search_results.items():
            validation_results[parameter] = self._result_is_valid(parameter, result)

        # Now that we know the search results are valid, we get the values
        # they represent for our dice using each parameter's associated
        # function on its search result.
        dice = {}
        for parameter, is_valid in validation_results.items():
            search_result = search_results[parameter]
            func = self._processing_funcs[parameter]
            default = self._default_values[parameter]

            dice[parameter] = func(search_result) if is_valid else default

        # Now that we know our dice values, we check them to make sure
        # No illegal values are present.
        self._values_are_valid(dice["sides"], dice["count"], dice["exploding"])

        return dice

    def _result_is_valid(self, parameter: str, search_result: list[str]) -> bool:
        """
        Search results (of the regex search) are validated by comparing their
        length to a series of requirements and is_invalid comparison function
        pairs that are unique to each parameter. If is_invalid is True, then
        the consequence will determine whether the function returns False (in
        this case the parameter is optional and wasn't used) or an exception
        is raised (in the case of a syntax violating input or a missing
         """
        length = len(search_result)
        for is_invalid, requirement, consequence in self._result_validation_args[parameter]:
            if is_invalid(length, requirement):
                if consequence is Exception:
                    raise ValueError(f"Invalid search_result length for {parameter}:\n"
                                     f"{search_result=}\n{is_invalid=}\n{requirement=}")
                else:
                    return False
        return True

    @staticmethod
    def _values_are_valid(sides: int, count: int, exploding: int | float) -> None:
        """
        Raises an exception if the dice parameters sides, count, or exploding
        have fatal issues with their values.
        """
        if sides <= 0:
            raise ValueError(f"sides must be greater than zero: {sides=}")
        elif count <= 0:
            raise ValueError(f"count must be greater than zero: {count=}")
        elif exploding <= 1:
            raise ValueError(f"Exploding value must be greater than 1: {exploding=}")

    @staticmethod
    def _extract_int(substring: str) -> int:
        """
        Extracts all numerical characters, in the order they appear, then
        concatenates and runs the int() function.
        """
        regex = re.compile("\\d")
        search = regex.findall(substring)
        return int("".join(search))


class FastRoller(Roller):
    """
    A diceroller that parses dice once during init, for use explicitly in
    programs that would loop a large number of times, rolling the same type of
    dice repeatedly. Going through the parsing phase every time would be
    wasteful. I wonder if it'll be a lot faster?
    """
