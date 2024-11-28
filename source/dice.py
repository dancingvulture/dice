"""A Module containing some dice rollers."""


import math
import operator
import random
import re

import numpy as np


class Roller:
    """
    A die roller that can take readable string inputs ('1d20', '3d6', etc.)
    into its rolling methods (sum or pool). It uses the following syntax:
    [N]dS[eX][^][v]
        - Optional parameters are bracketed.
        - [N] Number of dice to roll, if not entered it default to 1.
        - [eX] exploding dice, where X is the number a result must be equal to
          or greater than in order to explode.
        - [^] advantage, one advantage for every + symbol.
        - [v] disadvantage, one disadvantage for every - symbol.
        - [eX] and [^v] are mutually exclusive, rolling with both is not
        - currently supported.
    """
    def __init__(self, randint_method=None, advantage_method=None):
        # PREFERENCES
        random_generators = {
            None: lambda c, s: [random.randint(1, s) for _ in range(c)],
            "numpy": lambda c, s: list(np.random.randint(1, s, c))
        }
        self._basic_roll = random_generators[randint_method]

        advantage_methods = {
            None: self._add_dice_adv,
            "roll all": self._roll_all_adv,
        }
        self._roll_advantage_dice = advantage_methods[advantage_method]

        # CONSTANTS
        self._advantage_symbol = "^"
        self._disadvantage_symbol = "v"

        # Generate the regex functions used to parse dice inputs.
        patterns = {
            "count": "^\\d+",
            "sides": "d\\d*",
            "exploding": "e\\d*",
            "advantage": f"[//{self._advantage_symbol}{self._disadvantage_symbol}]",
        }
        self._regex_funcs = {}
        for parameter, pattern in patterns.items():
            self._regex_funcs[parameter] = re.compile(pattern).findall

        # A few hardcoded attributes that will be needed to validate regex
        # search results.
        self._result_validation_args = {
            "count": ((operator.gt, 1, Exception), (operator.ne, 1, False)),
            "sides": ((operator.ne, 1, Exception),),
            "exploding": ((operator.gt, 1, Exception), (operator.ne, 1, False)),
            "advantage": ((operator.eq, 0, False),),
        }

        # Default values for each parameter.
        self._default_values = {
            "count": 1,
            "sides": 0,
            "exploding": math.inf,
            "advantage": 0,
        }

        # Functions used to process regex search results for each parameter.
        self._processing_funcs = {
            "count": lambda x: int(x[0]),
            "sides": lambda x: self._extract_int(x[0]),
            "exploding": lambda x: self._extract_int(x[0]),
            "advantage": lambda x: self._determine_advantage(x),
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
              advantage: int) -> list[int]:
        """
        Ths is where the magic happens.
        """
        if exploding < math.inf:
            roll = self._roll_exploding_dice(count, sides, exploding)
        elif advantage:
            # noinspection PyArgumentList
            roll = self._roll_advantage_dice(count, sides, advantage)
        else:
            roll = self._basic_roll(count, sides)
        return roll

    def _roll_exploding_dice(self, count: int, sides: int, exploding: int | float
                             ) -> list[int]:
        """
        Roll dice that explode (causing a bonus dice to be rolled) whenever
        a die meets or exceeds a set value.
        """
        roll = self._basic_roll(count, sides)
        explosion_dice = []
        for value in roll:
            if value >= exploding:
                extra_dice = self._basic_roll(1, sides)
                while extra_dice[-1] >= exploding:
                    extra_dice += self._basic_roll(1, sides)
                explosion_dice += extra_dice
        return roll + explosion_dice

    def _add_dice_adv(self, count: int, sides: int, advantage: int) -> list[int]:
        """
        Advantage implementation where n dice are added, and the highest/lowest
        n dice are kept.
        """
        roll = self._basic_roll(count + (abs_adv := abs(advantage)), sides)
        reverse = True if advantage < 0 else False
        return sorted(roll, reverse=reverse)[abs_adv:]

    def _roll_all_adv(self, count: int, sides: int, advantage: int) -> list[int]:
        """
        Advantage implementation where all dice are rolled n times, and list
        with the greatest/lowest sum is chosen.
        """
        rolls = []
        for _ in range(abs(advantage)):
            rolls.append(self._basic_roll(count, sides))

        reverse = True if advantage > 0 else False
        return sorted(rolls, key=sum, reverse=reverse)[0]

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
        self._values_are_valid(dice)

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
    def _values_are_valid(dice: dict[str, int | None]) -> None:
        """
        Raises an exception if the dice parameters sides, count, or exploding
        have fatal issues with their values.
        """
        if dice["sides"] <= 0:
            raise ValueError(f"sides must be greater than zero: {dice["sides"]=}")
        elif dice["count"] <= 0:
            raise ValueError(f"count must be greater than zero: {dice["count"]=}")
        elif dice["exploding"] <= 1:
            raise ValueError(f"Exploding value must be greater than 1: {dice["exploding"]=}")
        elif dice["exploding"] < math.inf and dice["advantage"] != 0:
            raise ValueError(f"Exploding dice arguments and advantage cannot both "
                             f"be used for the same input.")

    @staticmethod
    def _extract_int(substring: str) -> int:
        """
        Extracts all numerical characters, in the order they appear, then
        concatenates and runs the int() function.
        """
        regex = re.compile("\\d")
        search = regex.findall(substring)
        return int("".join(search))

    def _determine_advantage(self, search_result: list[str]) -> int:
        """
        Count the advantage and disadvantage symbols present in the search
        result, subtract the number of advantage symbols from the number of
        disadvantage symbols and return the resulting int.
        """
        advantage = 0
        for symbol in search_result:
            if symbol == self._advantage_symbol:
                advantage += 1
            elif symbol == self._disadvantage_symbol:
                advantage -= 1
            else:
                raise ValueError(f"Invalid symbol: {symbol}")
        return advantage


class FastRoller(Roller):
    """
    A die roller that parses dice once during init, for use explicitly in
    programs that would loop a large number of times, rolling the same type of
    dice repeatedly. Going through the parsing phase every time would be
    wasteful. I wonder if it'll be a lot faster?
    """
    def __init__(self, dice_input, *, randint_method=None, advantage_method=None):
        super().__init__( randint_method=randint_method,
                          advantage_method=advantage_method)
        self._dice = self._parse_dice(dice_input)

    def pool(self) -> list:
        return self._roll(*self._dice.values())

    def sum(self) -> int:
        return sum(self._roll(*self._dice.values()))

