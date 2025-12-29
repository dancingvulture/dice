"""
Try out a bunch of random inputs.
"""


from rich.progress import Progress
import dice
import src.randomize as rnd


def random_input(trials: int, suppress_print: bool) -> None:
    """
    Do any number of random inputs, either to mass test and hunt for
    exceptions, or to just view inputs and outputs.
    """
    with Progress() as progress:
        if not suppress_print:
            task = progress.add_task("Rolling dice...", total=trials)
        _execute_random_input(suppress_print)


def _execute_random_input(suppress_print: bool) -> None:
    """
    Execute a single random dice roll with the help of the input randomizer.
    Prints the outcome to stdout if printing isn't suppressed, and if an
    exception of any kind occurs it will force a print of the last input, and
    will also pickle the python built-in random state at the time of the
    input.
    """


