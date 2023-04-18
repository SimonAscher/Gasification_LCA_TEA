import pickle

from functions.general.utility import get_project_root


def get_correct_sigma(prediction, output_label):
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
    root_path = get_project_root()
    file_path = str(root_path) + r"\data\prediction_boundaries_and_errors_df"
    with open(file_path, "rb") as f:
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
