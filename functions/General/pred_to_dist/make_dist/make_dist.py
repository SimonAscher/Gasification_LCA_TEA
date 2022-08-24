from config import settings
import numpy as np


def make_dist(mean, sigma, dist_type="gaussian", length_array: int = settings.background.iterations_MC,
              random_state: int = settings.background.random_seed):
    """
    Function to turn a singular predicted value to a distribution.

    Parameters
    ----------

    mean: float
        Mean value of the distribution.
    sigma: float
        Standard deviation of the distribution.
    dist_type: str
        Specifies the type of distribution which is to be created.
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
    if dist_type == "gaussian":
        np.random.seed(random_state)  # set random seed
        distribution = np.random.default_rng().normal(loc=mean, scale=sigma,
                                                      size=length_array)  # create distribution array

    else:
        print("Warning: Distribution type not supported")

    return distribution
