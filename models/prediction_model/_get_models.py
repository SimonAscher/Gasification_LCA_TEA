import pickle

from config import settings
from functions.general.utility import get_project_root

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

    # Get file path to GBR data
    project_root = get_project_root()
    full_file_path = str(project_root) + r"\data\GBR_performance_summary"

    # Load performance summary object
    perf_summary = pickle.load(open(full_file_path, "rb"))

    # %% Extract models for all outputs

    # Get column labels of performance summary object
    column_labels = settings.labels.output_data

    models_dict = {}  # initialise dictionary to store loaded models in

    # Extract and store models
    for count, models in enumerate(column_labels):
        models_dict[models] = pickle.loads(perf_summary[models]['model'])

    return models_dict
