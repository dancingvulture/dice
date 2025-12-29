"""Tests for the dice module."""


from src.command_line import parse_arguments
import src.tests as tests


def main():
    args = parse_arguments()
    if args.test == "random-input":
        tests.random_input(args.trials, args.suppress_print)
    else:
        raise Exception(f"Invalid test: {args.test}")


if __name__ == "__main__":
    main()
