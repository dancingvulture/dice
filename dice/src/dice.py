"""A Module containing some dice rollers."""


import random
import re
import operator
from copy import deepcopy
import numpy as np


class Roller:
    """
    A die roller that can take readable string inputs ('1d20', '3d6', etc.)
    into its rolling methods (sum or pool). It uses the following syntax:

        [count]d[sides][exploding][advantage][disadvantage][>][target]

        - [count] Number of dice to roll, if not entered it default to 1.
        - [sides] Number of sides the dice has.
        - [exploding] exploding dice, where X is the number a result must be
          equal to or greater than in order to explode.
        - [advantage] one advantage for every ^ symbol.
        - [disadvantage] one disadvantage for every v symbol.
        - [>] include this symbol only if a target is also specified.
        - [target] for advantage systems that are trying to get a target
          number.

    Note also that:
        - Any of these parameters can be entered as keyword arguments instead,
          in case of a conflict, keyword arguments take priority.
        - [exploding] and [advantage/disadvantage] are mutually exclusive,
          rolling with both is not currently supported.
    """
    def __init__(self, randint_method="builtin-randint", advantage_method="add-dice",
                 roll_method="roll-over"):
        # PREFERENCES
        self._randint_method = randint_method
        self._random_generators = {
            "builtin-randint": self._builtin_randint,
            "numpy": self._numpy_randint,
        }

        advantage_methods = {
            "add-dice": self._add_dice_adv,
            "roll-all": self._roll_all_adv,
            "whitehack": self._whitehack_adv,
        }
        self._advantage_method = advantage_method
        self._roll_advantage_dice = advantage_methods[advantage_method]
        self._roll_method = roll_method

        self._roll_functions = {
            "advantage": {
                "add-dice": self._add_dice_adv,
                "roll-all": self._roll_all_adv,
                "whitehack": self._whitehack_adv,
            },
            "basic-roll": self._basic_roll,
            "exploding": self._roll_exploding_dice,
        }

        # CONSTANTS
        self._advantage_symbol = "^"
        self._disadvantage_symbol = "v"

        # Generate the regex functions used to parse dice inputs.
        patterns = {
            "count": "^\\d+",
            "sides": "d\\d*",
            "exploding": "e\\d*",
            "advantage": f"[//{self._advantage_symbol}{self._disadvantage_symbol}]",
            "target": ">\\d*",
        }
        self._regex_funcs = {}
        for parameter, pattern in patterns.items():
            self._regex_funcs[parameter] = re.compile(pattern).findall

        # Functions used to process regex search results for each parameter.
        self._processing_funcs = {
            "count": lambda x: int(x[0]),
            "sides": lambda x: self._extract_int(x[0]),
            "exploding": lambda x: self._extract_int(x[0]),
            "advantage": lambda x: self._determine_advantage(x),
            "target": lambda x: self._extract_int(x[0]),
        }

        # Needed parameter validation and error raising.
        self._parameter_value_requirements_and_error_messages = {
            "sides": (
                (operator.gt, 0),
                "sides must be greater than zero: sides = {}",
            ),
            "count": (
                (operator.gt, 0),
                "count must be greater than zero: count = {}",
            ),
            "exploding": (
                (operator.gt, 1),
                "exploding value must be greater than 1: exploding = {}"
            ),
            "target": (
                (operator.ne, "should always evaluate to true"),
                "how did this error happen? There are no invalid target values."
            ),
            "advantage": (
                (operator.ne, 0),
                "advantage shouldn't be in the dice dict if it's equal to zero"
            )
        }

    def pool(self, dice_input: str, **kwargs) -> list[int]:
        """
        Roll the dice, get the result as a list.
        """
        dice = self._parse_dice(dice_input, **kwargs)
        return self._roll(**dice)

    def sum(self, dice_input: str, **kwargs) -> int:
        """
        Roll the dice then add them all together.
        """
        return sum(self.pool(dice_input, **kwargs))

    def _roll(self, **kwargs) -> list[int]:
        """
        There are actually many different private rolling methods, this method
        just chooses the appropriate one and passes whatever arguments it
        needs into the function.
        """
        if "advantage" in kwargs:
            roll = self._roll_functions["advantage"][self._advantage_method](**kwargs)
            random.shuffle(roll)  # Unsorting the final result.

        elif "exploding" in kwargs:
            roll = self._roll_functions["exploding"](**kwargs)

        else:
            roll = self._roll_functions["basic-roll"](**kwargs)

        return roll

    def _basic_roll(self, count: int, sides: int) -> list[int]:
        """
        Your most basic roll! All roll methods will end up using this in
        some way. The random integer method is determined at init.
        """
        return self._random_generators[self._randint_method](count, sides)

    @staticmethod
    def _builtin_randint(count: int, sides: int) -> list[int]:
        """
        Uses python's builtin random.randint() function.
        """
        return [random.randint(1, sides) for _ in range(count)]

    @staticmethod
    def _numpy_randint(count: int, sides: int) -> list[int]:
        """
        Uses numpy's random int array generator.
        """
        return list(np.random.randint(1, sides, count))

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
        reverse = self._is_reversed(advantage)
        return sorted(roll, reverse=reverse)[:-abs_adv]

    def _roll_all_adv(self, count: int, sides: int, advantage: int) -> iter:
        """
        Advantage implementation where all dice are rolled n times, and list
        with the greatest/lowest sum is chosen.
        """
        rolls = []
        for _ in range(abs(advantage)):
            rolls.append(self._basic_roll(count, sides))
        reverse = self._is_reversed(advantage)
        return sorted(rolls, key=sum, reverse=reverse)[-1]

    def _whitehack_adv(self, count: int, sides: int, advantage: int,
                       target: int) -> list[int]:
        """
        Implementation of advantage for whitehack.
        """
        rolls = self._basic_roll(count + (abs_adv := abs(advantage)), sides)

        rolls = sorted(rolls, reverse=True)
        successful_rolls = []
        failed_rolls = []
        for result in rolls:
            if result > target:
                failed_rolls.append(result)
            else:
                successful_rolls.append(result)

        if advantage > 0:
            # We have advantage, so we chop off the worst rolls.
            rolls = successful_rolls + failed_rolls
        else:
            # We have disadvantage, so we chop off the best rolls.
            rolls = failed_rolls + successful_rolls

        # Slicing out the last N = abs(advantage) results.
        return rolls[:-abs_adv]

    def _is_reversed(self, advantage: int) -> bool:
        """
        Determine whether the sorted list is reversed or not. This always
        biases putting the 'worst' values first. And being slightly more
        specific, we are deciding IF the list should be reversed or not.
        Or, in other words, deciding whether we're keeping the highest
        values or the lowest values.
        """
        # Two variables, each with two possible values, so four cases total.
        # Note also: reverse=True means the highest values will be first
        #            reverse=False means the lowest values will be first
        if ((advantage > 0 and self._roll_method == "roll-over")
                or
            (advantage < 0 and self._roll_method == "roll-under")):
            # We have advantage and we want to roll high. (we get what we want)
            # or
            # We have disadvantage and we want to roll low. (we don't get what we want)
            return True
        elif advantage == 0:
            raise ValueError("You should not be running this method if"
                             " advantage=0")
        else:
            # We have advantage and we want to roll low. (we get what we want)
            # We have disadvantage and we want to roll high. (we don't get what we want)
            return False

    def _parse_dice(self, dice_input: str, **kwargs) -> dict[str, int]:
        """
        Extract information from a dice-string input.
        """
        # First we do a regex search for each parameter.
        search_results = {}
        for parameter, findall in self._regex_funcs.items():
            search_results[parameter] = findall(dice_input.casefold())

        # Here we add any dice arguments we got from key word arguments.
        # then we take whatever results (if any) from dice_input and process
        # the results with each one's dedicated processing function.
        dice = deepcopy(kwargs)
        for parameter, results in search_results.items():
            func = self._processing_funcs[parameter]

            # Run the processing func on any non-empty search.
            # Also, we explicitly make sure dice_input results don't overwrite
            # anything passed in as a key world argument.
            if results and parameter not in kwargs:
                dice[parameter] = func(results)

        # Now that we know our dice values, we check them to make sure
        # No illegal values are present.

        # Then we handle some exceptional situations.
        if "count" not in dice: dice["count"] = 1  # Only parameter with a default value.
        if "advantage" in dice and dice["advantage"] == 0: del dice["advantage"]
        if "target" in dice and "advantage" not in dice: del dice["target"]

        self._values_are_valid(dice)

        return dice

    def _values_are_valid(self, dice: dict[str, int]) -> None:
        """
        Makes sure all parameters are integers, that the integer values are
        within certain bounds depending on the parameter, along with other checks.
        """
        # First we make sure each parameter's value is an integer, and the
        # integer passes an inequality, if not, raise an exception and show an
        # error message.
        req_and_error = self._parameter_value_requirements_and_error_messages
        for parameter, value in dice.items():
            if not isinstance(value, int):
                raise ValueError(f"Parameter {parameter} must be int: {value=}")

            (oper, req), error_msg = req_and_error[parameter]
            if not oper(value, req):
                raise ValueError(error_msg.format(value))

        # Then we make sure we aren't rolling exploding advantage dice.
        if "exploding" in dice and "advantage" in dice:
            raise ValueError(f"Exploding dice arguments and advantage cannot both "
                             f"be used for the same input.")

        if (self._advantage_method == "whitehack" and "advantage" in dice 
            and "target" not in dice):
            raise ValueError("If using whitehack's advantage method you must"
                             " specify a target.")

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
        if self._get_dice_count(dice_input) >= 20:  # Testing on laptop shows this is the point
            randint_method = "numpy"                # where it becomes more efficient than the
                                                    # builtin method.
        super().__init__(randint_method=randint_method,
                         advantage_method=advantage_method)
        self._dice = self._parse_dice(dice_input)

    def pool(self) -> list:
        """
        Roll the dice, get the result as a list. Takes no arguments.
        """
        return self._roll(**self._dice)

    def sum(self) -> int:
        """
        Roll the dice then add them all together. Takes no arguments.
        """
        return sum(self._roll(**self._dice))

    @staticmethod
    def _get_dice_count(dice_input: str) -> int:
        """
        Get the dice count from dice input. This is dumber than parse
        dice, if it finds no match it assumes there is only one die.
        """
        match = re.compile("^\\d+").search(dice_input)
        if match is None:
            return 1
        else:
            slc = slice(*match.span())
            return int(dice_input[slc])

