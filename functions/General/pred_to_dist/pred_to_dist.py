from functions.general.pred_to_dist.get_correct_sigma import get_correct_sigma
from functions.general.pred_to_dist.make_dist.make_dist import *


# TODO: Why do I have to call these differently? See line 25 - sigma =

def pred_to_dist(prediction, output_label):
    """
    Wrapper function to make a distribution with the correct sigma value and default distribution type and MC length.

    Parameters
    ----------
    prediction: float
        The predicted value for the corresponding function output.
    output_label: float
        String defining the target/output variable.

    Returns
    -------
    array
        Numpy array of distribution values.
    """

    # Get correct error value
    sigma = get_correct_sigma.get_correct_sigma(prediction, output_label)
    distribution = make_dist(prediction, sigma)

    return distribution


