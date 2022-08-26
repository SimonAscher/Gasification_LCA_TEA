import pandas as pd


def make_predictions(models_dict, data, output_selector="all"):
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
    # Convert data to right format
    data = [data]

    # Define function to check if data is in right format (i.e. pandas dataframe)
    def to_df(data):
        """
        Check if data is given as pandas dataframe - otherwise turn into one.
        Parameters
        ----------
        data :
            Input data used to make predictions on.

        Returns
        -------
        pandas.DataFrame
        """

        # Check whether object is already a pandas DataFrame
        if isinstance(data, pd.DataFrame):
            pass
        else:
            # Define labels of data
            from config import settings
            input_data_labels = settings.labels.input_data

            # Change data to pandas dataframe
            data = pd.DataFrame(data=data,
                                index=["data"],
                                columns=input_data_labels)
        return data

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
