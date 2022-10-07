from functions.general.predictions_to_distributions import utils
from functions.general.predictions_to_distributions.utils import get_correct_sigma
from functions.MC import make_dist
from config import settings
from configs import gaussian


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
    # Get distribution
    distribution = make_dist(gaussian(prediction, sigma))

    return distribution


def get_all_prediction_distributions(predictions):
    """
    Wrapper function to get prediction distributions for all outputs.
    Parameters
    ----------
    predictions: dict
        Dictionary of predictions for all 10 model outputs.

    Returns
    -------
    dict
        Dictionary of distribution associated with each model output.
    """

    output_labels = settings.labels.output_data  # get labels
    distributions = {}  # initialise distributions dictionary

    # Get distributions for each output and store in dictionary
    for count, output_label in enumerate(output_labels):
        prediction = predictions[output_label]
        distribution = pred_to_dist(prediction, output_label)
        distributions[output_label] = list(distribution)

    return distributions
