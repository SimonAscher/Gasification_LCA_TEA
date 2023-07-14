import numpy as np

from dynaconf.utils.boxing import DynaBox
from config import settings
from objects import triangular_dist_maker, gaussian_dist_maker, fixed_dist_maker, range_dist_maker


def to_fixed_MC_array(value, no_iterations=settings.user_inputs.general.MC_iterations):
    """
    Convenience function to turn any value into a repeating array the length of Monte Carlo iterations.

    Parameters
    ----------
    value: float
        Value which is to be repeated.

    no_iterations: float
        Number of iterations. Default value loaded from settings.

    Returns
    -------
    np.array
        Numpy array repeating the input value.
    """
    mc_array = np.repeat(value, no_iterations)
    return mc_array


def get_distribution_draws(distribution_maker, length_array=settings.user_inputs.general.MC_iterations,
                           random_state: int = settings.background.random_seed):
    """
    Function to get draws from a given distribution type (e.g. gaussian, triangular, fixed).

    Parameters
    ----------
    distribution_maker: triangular_dist_maker | gaussian_dist_maker | fixed_dist_maker | range_dist_maker
        Named tuple defining the variables of the distribution. Defined in objects/generic_objects.py.
        Contains variables (e.g. mean, std, lower, upper, mode) defining the given distribution.
    length_array: int
        Length of created array. Default value is the number of Monte Carlo iterations loaded from settings.
        If set to 1 only a single value is drawn from distribution.
    random_state: int
        Random seed to be used in analysis. Default value defined in settings.

    Returns
    -------
    np.array | float
        Numpy array of distribution values or float if length_array has been set as 1.
    """
    # np.random.seed(random_state)  # set random seed

    if isinstance(distribution_maker, gaussian_dist_maker):
        distribution = np.random.default_rng().normal(loc=distribution_maker.mean, scale=distribution_maker.std,
                                                      size=length_array)

    elif isinstance(distribution_maker, triangular_dist_maker):
        distribution = np.random.default_rng().triangular(left=distribution_maker.lower, mode=distribution_maker.mode,
                                                          right=distribution_maker.upper, size=length_array)

    elif isinstance(distribution_maker, fixed_dist_maker):
        distribution = to_fixed_MC_array(value=distribution_maker.value, no_iterations=length_array)

    elif isinstance(distribution_maker, range_dist_maker):
        distribution = np.random.default_rng().uniform(low=distribution_maker.low, high=distribution_maker.high,
                                                       size=length_array)

    else:
        raise ValueError("Warning: Distribution type not supported. Currently only 'gaussian_dist_maker' supported.")

    if length_array == 1:
        distribution = float(distribution)

    return distribution


def dist_maker_from_settings(location):
    """
    Takes distribution type and parameters stored in settings object and turns them back into a distribution maker.

    Parameters
    ----------
    location: DynaBox
        Location in settings object where the distribution type and its parameters are defined.

    Returns
    -------
    triangular_dist_maker | gaussian_dist_maker | range_dist_maker | fixed_dist_maker
        Distribution maker based on the parameters stored in the given storage location.
    """

    # Initialise variables
    dist_maker = None

    # Check which distribution type is present and create dist_maker accordingly.
    if location.distribution_type == "fixed":
        dist_maker = fixed_dist_maker(value=location.value)
    elif location.distribution_type == "range":
        dist_maker = range_dist_maker(low=location.low, high=location.high)
    elif location.distribution_type == "triangular":
        dist_maker = triangular_dist_maker(lower=location.lower, mode=location.mode, upper=location.upper)

    elif location.distribution_type == "gaussian":
        dist_maker = gaussian_dist_maker(mean=location.mean, std=location.std)
    else:
        ValueError("Distribution type not supported.")

    return dist_maker
