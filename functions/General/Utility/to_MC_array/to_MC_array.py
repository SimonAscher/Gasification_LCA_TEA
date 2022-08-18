import numpy as np


def to_mc_array(value: float, no_iterations: float) -> object:
    """
    Convenience function to turn any value into a repeating array the length of Monte Carlo iterations.

    Parameters
    ----------
    value: float
        Value which is to be repeated

    no_iterations: float
        Number of iterations

    Returns
    -------
    array
        Numpy array repeating the input value
    """
    # TODO: Add default value for no_iterations based on settings file once settings file has been set up

    mc_array = np.repeat(value, no_iterations)
    return mc_array
