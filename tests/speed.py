from rich.progress import Progress
from datetime import datetime
from dice.src.dice import Roller, FastRoller


def fast_roller_speed_test(dice_input: str, trials: int) -> None:
    """
    Simple test of FastRoller speed.
    """
    with Progress() as progress:
        task = progress.add_task("Rolling slow...", total=trials)
        n_start = datetime.now()
        n_roller = Roller()
        for index in range(trials):
            n_roller.pool(dice_input)
            progress.advance(task)
        n_end = datetime.now()
        n_runtime = n_end - n_start

    with Progress() as progress:
        task = progress.add_task("Rolling fast...", total=trials)
        f_start = datetime.now()
        f_roller = FastRoller(dice_input)
        for index in range(trials):
            f_roller.pool()
            progress.advance(task)
        f_end = datetime.now()
        f_runtime = f_end - f_start

    print(f"Dice Input: {dice_input}, Trials: {trials:,}")
    print(f"    Roller runtime: {n_runtime}")
    print(f"FastRoller runtime: {f_runtime}")
    print(f"        Difference: {n_runtime - f_runtime}")
