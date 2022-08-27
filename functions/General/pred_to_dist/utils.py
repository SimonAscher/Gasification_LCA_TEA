import pickle
import numpy as np
from config import settings


def get_correct_sigma(prediction: float, output_label: str) -> float:
    """
    Function to get the error value associated with a prediction.

    Parameters
    ----------
    prediction: float
        The predicted value for the corresponding function output.
    output_label: float
        String defining the target/output variable.

    Returns
    -------
    float
        Correct error value to be used in fitting distribution.
    """

    # Load dataframe containing errors
    with open(r"C:\Users\2270577A\PycharmProjects\PhD_LCA_TEA\data\prediction_boundaries_and_errors_df", "rb") as f:
        boundaries_errors_df = pickle.load(f)

    # Get boundaries and errors (sigmas)
    boundaries = boundaries_errors_df.loc["boundaries"][output_label]
    sigmas = boundaries_errors_df.loc["RMSE"][output_label]

    # Loop to select correct error for predicted value
    correct_sigma = []  # initialise variable
    for count, boundary in enumerate(boundaries):
        if prediction < boundary:  # stop on first iteration where boundary is larger than predicted value.
            correct_sigma = sigmas[count]
            break
        if count == len(boundaries) - 1:  # condition for prediction larger than the largest boundary value.
            correct_sigma = sigmas[count + 1]

    return correct_sigma


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
        #np.random.seed(random_state)  # set random seed
        distribution = np.random.default_rng().normal(loc=mean, scale=sigma,
                                                      size=length_array)  # create distribution array

    else:
        print("Warning: Distribution type not supported")
        # TODO: Turn this warning message into proper warning.
    return distribution
