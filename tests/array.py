import csv

from rich.progress import Progress
import numpy as np
from datetime import datetime
from source.dice import Roller


class RandomArrayTest:
    """
    Checking how large of a die pool we need for the numpy method to be
    more effective than the built-in random.
    """
    def __init__(self, array_sizes: list[int], trials: int):
        self._trials = trials
        self._sizes = array_sizes
        self._methods = ("built-in", "numpy")
        self._data = {
            "built-in": {size: None for size in array_sizes},
            "numpy": {size: None for size in array_sizes},
        }

        with Progress() as progress:
            progress.add_task("Pre-generating dice side-counts")
            self._sides = np.random.default_rng().integers(2, 1000, trials)

    def generate_data(self):
        """
        Generate dice data for each array_size.
        """
        for size in self._sizes:
            for method in self._methods:
                self._data[method][size] = self._measure_roll_time(method, size)

    def _measure_roll_time(self, method: str, size: int) -> float:
        """
        Measures the time it takes for the roller to roll a number of
        dice using the given method and size of the roll (i.e. how many
        dice are throw).
        """
        # Initialize roller.
        if method == "built-in":
            roller = Roller(randint_method=None)
        else:
            roller = Roller(randint_method=method)

        with Progress() as progress:
            task = progress.add_task(
                f"Rolling {size} dice at once with {method}...",
                total=self._trials
            )

            start = datetime.now()
            for index in range(self._trials):
                roller.pool(f"{size}d{self._sides[index]}")
                progress.advance(task)
            end = datetime.now()

            difference = end - start
            return difference.total_seconds()

    def save_to_csv(self, filename=None):
        """
        Save data stored in the class to a CSV. With rows giving the
        sizes in ascending order, and each column saying what each method
        got for a given size.
        """
        if filename is None:
            filename = self._generate_filename("csv")

        with open(filename, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Trials:", self._trials])
            writer.writerow(["size"] + [method for method in self._methods])  # Column headers.

            rows = []
            for size in self._sizes:
                row = [size]
                for method in self._methods:
                    row.append(self._data[method][size])
                rows.append(row)
            writer.writerows(rows)

    @staticmethod
    def _generate_filename(filetype: str) -> str:
        """
        Generates a filename based off the current time.
        """
        time_str = datetime.now().isoformat().split(".")[0]
        while (index := time_str.find(":")) != -1:
            time_str = time_str[:index] + "-" + time_str[index + 1:]

        filepath = "tests/array data/"
        return filepath + time_str + "." + filetype
