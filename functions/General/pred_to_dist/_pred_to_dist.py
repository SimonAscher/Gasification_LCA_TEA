from functions.general.pred_to_dist import utils
from .utils import make_dist, get_correct_sigma

# TODO: Why do I have to call these differently? See line 25 - sigma = ... - FIX THIS

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
    sigma = get_correct_sigma(prediction, output_label)
    distribution = make_dist(prediction, sigma)

    return distribution
