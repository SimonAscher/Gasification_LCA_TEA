# Function that fetches models
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
    from config import settings
    column_labels = settings.labels.output_data

    models_dict = {}  # initialise dictionary to store loaded models in

    # Extract and store models
    for count, models in enumerate(column_labels):
        models_dict[models] = pickle.loads(perf_summary[models]['model'])

    return models_dict
