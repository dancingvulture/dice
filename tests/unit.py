from dice.src.dice import Roller, FastRoller


def unit_test(roller: str) -> None:
    """
    Testing various dice inputs.
    """
    dice_inputs = ['1d20', '1d100', '3d6', '1d20^', '1d20v', '4d33', '1d4e4',
                   '8d6e6', '2d6^^', '1d66e50', '1d666', '5d6^^', '8d8vvvv',
                   "d20", "1d10^v", "1d6^^^^^^", "1d6vvvvvv", "3d2e2", "2d4^"]
    if roller == "base":
        roller = Roller()
        for inp in dice_inputs:
            roll = roller.pool(inp)
            sum_ = sum(roll)
            print(f"{inp}: {roll}: {sum_}")

    elif roller == "fast":
        for inp in dice_inputs:
            roller = FastRoller(inp)
            roll = roller.pool()
            sum_ = sum(roll)
            print(f"{inp}: {roll}: {sum_}")

    else:
        raise ValueError(f"Invalid roller: {roller}")
