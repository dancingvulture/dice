"""
Try out a bunch of random inputs.
"""


from rich.progress import Progress
import traceback
import dice
import src.randomize as rnd
import src.random_state as rnd_state


def random_input(trials: int, suppress_print: bool) -> None:
    """
    Do any number of random inputs, either to mass test and hunt for
    exceptions, or to just view inputs and outputs.
    """
    with Progress() as progress:
        if suppress_print:
            task = progress.add_task("Rolling dice...", total=trials)
        for _ in range(trials):
            encountered_error = _execute_random_input(suppress_print)
            if encountered_error: break
            if suppress_print: progress.advance(task)


def _execute_random_input(suppress_print: bool) -> bool:
    """
    Execute a single random dice roll with the help of the input randomizer.
    Prints the outcome to stdout if printing isn't suppressed, and if an
    exception of any kind occurs it will force a print of the last input, and
    will also pickle the python built-in random state at the time of the
    input.
    """
    # Create random inputs, then save the state of the random module before
    # the roll.
    dice_str, dice_kwargs = rnd.dice_input()
    state = rnd_state.get()

    if not suppress_print:
        print(f"Input: {dice_str}")
        for key, value in dice_kwargs.items():
            print(f" -    {key}: {value}")

    try:
        roll = dice.pool(dice_str, **dice_kwargs)
        sum_ = sum(roll)
    except Exception as exc:
        # If any exception happens, I want the last input and the random state,
        # That way the bug can be recreated. Then we set the state to the way
        # it was before the exception, then cause the exception to happen again.
        last_input = f"Last input: {dice_str}\n"
        for key, value in dice_kwargs.items():
            last_input += f" -    {key}: {value}\n"
        rnd_state.save(state)
        print("\nTraceback:")
        traceback.print_tb(exc.__traceback__)
        print()
        print(last_input)
        return True

    if not suppress_print: print(f"roll: {roll}: {sum_}", end="\n\n")
    return False