def get_models():
    """
    Loads performance summary dataframe and extracts models from that.

    Returns
    -------
    dict
        Prediction models in a dictionary.
    """

    # %% Load dataframe with models stored

    # Get directory path
    import os

    directory = os.getcwd()
    # Specify filename
    filename = "GBR_performance_summary"

    # Show full filepath
    full_file_path = directory + r"\\data\\" + filename
    # print("Full path to file:", full_file_path)

    # Load performance summary object
    import pickle
    perf_summary = pickle.load(open(full_file_path, "rb"))

    # %% Extract models for all outputs

    # Get column labels of performance summary object
    column_labels = perf_summary.columns

    models_dict = {}  # initialise dictionary to store loaded models in

    # Extract and store models
    for count, models in enumerate(column_labels):
        models_dict[models] = pickle.loads(perf_summary[models]['model'])

    return models_dict


# %% Function that actually makes predictions

def make_predictions(models_dict, data):
    """

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
            input_data_labels = ['C [%daf]', 'H [%daf]', 'S [%daf]', 'Particle size [mm]', 'Ash [%db]', 'Moisture [%wb]',
                                 'Temperature [°C]', 'Operation (Batch/Continuous)', 'ER', 'Catalyst', 'Scale',
                                 'Agent_air', 'Agent_air + steam', 'Agent_other', 'Agent_oxygen', 'Agent_steam',
                                 'Reactor_fixed bed', 'Reactor_fluidised bed', 'Reactor_other', 'Bed_N/A',
                                 'Bed_alumina', 'Bed_olivine', 'Bed_other', 'Bed_silica']

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
