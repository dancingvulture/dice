"""Tests for the dice module."""


from source.dice import DiceRoller


def main():
    dice_inputs = ['1d20', '1d100', '3d6', '1d20+', '1d20-', '400d33', '1d4e4',
                   '8d6e6', '2d6++', '1d66e50', '1d666', '5d6++', '8d8----',
                   "d20"]
    roller = DiceRoller()
    for inp in dice_inputs:
        print(inp)
        roller.pool(inp)
        print()


if __name__ == "__main__":
    main()
