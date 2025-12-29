"""
Functions to get, set, and save the state of the python builtin randomizer.
"""


import random
import shelve
from datetime import datetime


_SHELF_NAME = "saved random states"


def get():
    """
    Get the current state of python's built-in random module.
    """
    return random.getstate()


def set(state=None) -> None:
    """
    Set the state to a given state, or (if inputting nothing), allow it to
    simply set a random seed.
    """
    if state:
        random.setstate(state)
        print("Random module state set with custom state")
    else:
        random.seed()
        print("Random module state set with random seed")


def save(state=None) -> None:
    """
    Save the random state to a shelf. If no arguments are passed it uses
    the current state.
    """
    if not state: state = random.getstate()
    with shelve.open(_SHELF_NAME) as db:
        key = str(len(db))
        db[key] = ((time := datetime.now()), state)
    print(f"Saved random state at time {time}")


def load(key=None, set_state=True):
    """
    Given the key, load the associated state from the shelF. Given no key,
    just load the last one. By default this sets the global random state to
    the loaded state.
    """
    with shelve.open(_SHELF_NAME) as db:
        if (size := len(db)) == 0: raise Exception("Cannot load from empty shelf")
        if not key: key = str(size - 1)

        time, state = db[key]

    if set_state:
        random.setstate(state)
        print(f"Loaded random state #{key}, created at {time}")

    return state


def show():
    """
    Show all random states currently saved.
    """
    display = ""
    with shelve.open(_SHELF_NAME) as db:
        for key, (time, _) in db.items():
            display += f"{key} -> State saved at {time}\n"
    print(display)
