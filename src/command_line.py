"""
Module containing everything needed to handle command line arguments.
"""


import argparse


_TRIALS_ARG = {
    "dest": "trials",
    "type": lambda x: int(float(x)),
    "help": "Number of trials to run",
}
_SUPPRESS_PRINT_NAME = ["-sp", "--suppress_print"]
_SUPPRESS_PRINT_ARGs = {
    "help": "Suppress most messages; intended for running a large number of trials",
    "action": "store_true",
}


def parse_arguments() -> argparse.Namespace:
    """
    Handle command line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="Dice Module Tester",
        description="Run a variety of tests on the dice module to make sure"
                    " it actually works."
    )
    subparsers = parser.add_subparsers(
        dest="test",
        help="Choose a test to run.",
    )
    parser.add_argument(
        "--load_random_state", "-lr",
        help=""
    )

    _add_random_input_parser(subparsers)

    return parser.parse_args()


def _add_random_input_parser(subparsers) -> None:
    """
    Parser for the random input test.
    """
    parser = subparsers.add_parser(
        "random-input",
        help="Run the dice roller with random inputs."
    )
    parser.add_argument(*_SUPPRESS_PRINT_NAME, **_SUPPRESS_PRINT_ARGs)
    parser.add_argument(**_TRIALS_ARG)

