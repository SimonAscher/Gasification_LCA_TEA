from config import settings
import numpy as np


def to_MC_array(value: float, no_iterations: int = settings.background.iterations_MC) -> object:
    """
    Convenience function to turn any value into a repeating array the length of Monte Carlo iterations.

    Parameters
    ----------
    value: float
        Value which is to be repeated

    no_iterations: float
        Number of iterations. Default value loaded from settings.

    Returns
    -------
    array
        Numpy array repeating the input value.
    """
    mc_array = np.repeat(value, no_iterations)
    return mc_array
