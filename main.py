"""Tests for the dice module."""


from tests.unit import unit_test
from tests.speed import fast_roller_speed_test
from tests.array import RandomArrayTest
import argparse


def parse_arguments() -> dict.items:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode")

    # Unit test
    unit_test_parser = subparsers.add_parser(
        "unit",
        help="Unit test for Roller",
    )

    # Fast roller speed test
    fast_roller_parser = subparsers.add_parser(
        "fast",
        help="Test how the FastRoller performs vs the normal one.",
    )
    fast_roller_parser.add_argument(
        "dice",
        help="Dice input for dice roller.",
    )
    fast_roller_parser.add_argument(
        "trials",
        type=lambda x: int(float(x)),
    )

    # Numpy v Python
    numpy_parser = subparsers.add_parser(
        "array",
        help="Compare how the builtin randint method performs against numpy's"
             " for various array sizes.",
    )
    numpy_parser.add_argument(
        "array_sizes",
        help="Put in a list, 1,2,3, or range 4-8; or a combination.",
        type=lambda x: _parse_range(x)
    )
    numpy_parser.add_argument(
        "trials",
        help="Number of trials per array size.",
        type=lambda x: int(float(x)),
    )

    args = parser.parse_args()
    return vars(args).values()


def _parse_range(inp: str) -> list[int]:
    """
    Meant to parse a command-line input that denotes a list of integers.
    Syntax is similar to page numbers, (i.e. 1-3,4,6,7).
    """
    step_list = []
    for piece in inp.split(","):
        if "-" in piece:
            start, stop = map(int, piece.split("-"))
            step_list.extend(range(start, stop + 1))
        else:
            step_list.append(int(piece))
    return step_list


def main():
    mode, *args = parse_arguments()

    if mode == "unit":
        unit_test()
    elif mode == "fast":
        fast_roller_speed_test(*args)
    elif mode == "array":
        test = RandomArrayTest(*args)
        test.generate_data()
        test.save_to_csv()
        print("Saved to file!")
    else:
        raise ValueError(f"Invalid mode: {mode}")


if __name__ == "__main__":
    main()
