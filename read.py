import sys

import sys
from typing import Callable


def process_input(func: Callable[[str, str], str]):
    """
    Process the command-line arguments and call the provided function with the arguments.

    Args:
        func (Callable[[str, ...str]]): A function to be called with the command-line arguments.
            Takes one or more string arguments and returns a value.

    Returns:
        Any: The result returned by the provided function, if not argument passed return None
    """

    result = None
    if len(sys.argv) > 1:
        # At least one argument has been passed
        first_argument = sys.argv[1]

        print('\nFirst argument: "' + first_argument + '"\n')

        if len(sys.argv) == 2:
            # Only one argument has been passed
            result = func(first_argument)
        else:
            # Two arguments or more have been passed
            second_argument = sys.argv[2]
            result = func(first_argument, second_argument)

    else:
        raise Exception("No arguments have been passed to the script: ", sys.argv[0], 'Number of args:', len(sys.argv))

    return result
