def make_predictions(models_dict, data):
    """
    Function that actually makes the predictions

    Parameters
    ----------
    models_dict
    data

    Returns
    -------

    """

    # Check if data is a pandas dataframe - if not try to turn into one
    def to_df(data):
        """
        Check if data is given as dataframe - otherwise turn into one.
        Parameters
        ----------
        data : Input data for which predictions are to be made.

        Returns
        -------
        pandas.DataFrame
        """
        import pandas as pd

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


    data = to_df(data)

    # Make predictions on data

    predictions = {} # initialise dictionary
    for count, model_label in enumerate(models_dict):
        prediction_model = models_dict[list(models_dict.keys())[count]] # load model
        prediction = prediction_model.predict(data) # make prediction
        predictions[model_label] = float(prediction) # store prediction

    return predictions
