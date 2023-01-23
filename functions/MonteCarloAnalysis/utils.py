from config import settings
import numpy as np
from configs import triangular, gaussian


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


def make_dist(values, length_array: int = settings.background.iterations_MC,
              random_state: int = settings.background.random_seed):
    """
    Function to turn a singular value to a distribution.

    Parameters
    ----------
    values: triangular or gaussian
        Named tuple of the type triangular or gaussian. Defined in configs/default_objects.py.
        Contains variables (e.g. mean, std, lower, upper, mode) defining the given distribution.
    length_array: int
        Length of created array. Default value is the number of Monte Carlo iterations loaded from settings.
    random_state: int
        Random seed to be used in analysis. Default value defined in settings.

    Returns
    -------
    array
        Numpy array of distribution values.
    """

    distribution = []  # initialise distribution array
    # np.random.seed(random_state)  # set random seed
    if isinstance(values, gaussian):
        distribution = np.random.default_rng().normal(loc=values.mean, scale=values.std,
                                                      size=length_array)
        # TODO: Consider implementing Latin Hypercube sampling or orthogonal sampling (for more info see:
        #  https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.qmc.LatinHypercube.html)
    elif isinstance(values, triangular):
        distribution = np.random.default_rng().triangular(left=values.lower, mode=values.mode, right=values.upper,
                                                          size=length_array)
    else:
        raise ValueError("Warning: Distribution type not supported. Currently only 'gaussian' supported.")

    return distribution
