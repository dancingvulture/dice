"""Tests for the dice module."""


from source.dice import _parse_dice


def main():
    dice_inputs = ['1d20', '1d100', '3d6', '1d20+', '1d20-', '400d33', '1d4e4',
                   '8d6e6', '2d6+', '1d66c', '1d666c', '5d6++', '8d8----']
    for inp in dice_inputs:
        print(inp)
        _parse_dice(inp)


if __name__ == "__main__":
    main()

