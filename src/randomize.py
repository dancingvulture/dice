"""
Random functions usable in various dice input tests.
"""


import random


def dice_input(string_only=False, kwargs_only=False,
               no_exploding=False, no_advantage=False,
               ) -> tuple[str, dict[str, int]]:
    """
    Get a random input for the dice function.
    """
    str_forms = {
        "count": lambda x: "{}".format(x),
        "sides": lambda x: "{}".format(x),
        "exploding": lambda x: "e{}".format(x),
        "advantage": lambda x: "^" * x,
        "disadvantage": lambda x: "v" * x,
        "target": lambda x: ">{}".format(x)
    }
    if no_exploding:
        del str_forms["exploding"]
    if no_advantage:
        del str_forms["advantage"]
        del str_forms["disadvantage"]
    parameter_names = list(str_forms.keys())

    # Get parameter values and forms.
    values = _get_parameter_values(parameter_names)
    name_count = len(parameter_names)
    parameters = {}
    for index in range(name_count):
        name = parameter_names[index]
        form = _get_parameter_form(string_only=string_only, kwargs_only=kwargs_only)
        value = values[index]
        parameters[name] = (form, value)

    # Build dice inputs.
    str_input = "{}d{}{}{}{}{}"
    kwarg_inputs = {}
    for name, (form, value) in parameters.items():
        if form == "str" and value is not None:
            str_input = str_input.replace("{}", str_forms[name](value), 1)

        elif form == "kwarg" and value is not None:
            str_input = str_input.replace("{}", "", 1)
            kwarg_inputs[name] = value

        else:
            str_input = str_input.replace("{}", "", 1)

    return str_input, kwarg_inputs


def _get_parameter_form(string_only=False, kwargs_only=False) -> str:
    """
    Randomly determines whether a parameter will be in the dice input or a kwarg.
    """
    if string_only:
        return "str"
    elif kwargs_only:
        return "kwarg"
    else:
        return random.choice(["str", "kwarg"])


def _get_parameter_values(parameter_names: list[str]) -> list[int | None]:
    """
    Given a parameter's name, get a random parameter value.
    """
    exploding = random.choice([True, False])
    values = {
        "count": random.randint(1, 100),
        "sides": (sides := random.randint(2, 1000)),
        "exploding": random.randint(2, sides) if exploding else None,
        "advantage": random.randint(0, 10) if not exploding else None,
        "disadvantage": random.randint(0, 10) if not exploding else None,
        "target": None,
    }
    try:
        return [val for val in values.values()]
    except KeyError:
        raise ValueError(f"Invalid parameter name: {parameter_names}")

