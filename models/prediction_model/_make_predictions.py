import pandas as pd

from models.prediction_model._get_models import get_models
from functions.general.utility import fetch_ML_inputs


def make_predictions(models_dict=None, data=None, output_selector="all"):
    """
    Function that makes prediction

    Parameters
    ----------
    models_dict: dict
        Dictionary of trained models.
    data: list
        Input data used to make predictions on.
    output_selector: list[str]
        Variable used to select outputs. By default, predictions are made for all outputs.

    Returns
    -------
    dict
        Dictionary of predictions.

    """
    # Get defaults
    if models_dict is None:
        models_dict = get_models()

    data = [data]

    if data is None:
        data = [fetch_ML_inputs()]

    # Define function to check if data is in right format (i.e. pandas dataframe)
    def to_df(data_to_check):
        """
        Check if data is given as pandas dataframe - otherwise turn into one.
        Parameters
        ----------
        data_to_check :
            Input data used to make predictions on.

        Returns
        -------
        pandas.DataFrame
        """

        # Check whether object is already a pandas DataFrame
        if isinstance(data_to_check, pd.DataFrame):
            pass
        else:
            # Define labels of data
            from config import settings
            input_data_labels = settings.labels.input_data

            # Change data to pandas dataframe
            data_to_check = pd.DataFrame(data=data_to_check,
                                         index=["data"],
                                         columns=input_data_labels)
        return data_to_check

    # Check if data is a pandas dataframe - if not call function and try to turn into one
    if not isinstance(data, pd.DataFrame):
        data = to_df(data)

    # Make predictions on data
    predictions = {}  # initialise dictionary

    if output_selector == "all":  # Default case which makes predictions for all outputs.
        pass
    else:  # Case for which outputs are specified
        models_dict = dict((k, models_dict[k]) for k in output_selector)

    for count, model_label in enumerate(models_dict):
        prediction_model = models_dict[list(models_dict.keys())[count]]  # load model
        prediction = prediction_model.predict(data)  # make prediction
        predictions[model_label] = float(prediction)  # store prediction

    return predictions
