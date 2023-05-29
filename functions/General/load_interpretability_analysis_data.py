import pickle

from functions.general.utility import get_project_root
from pandas import DataFrame


def load_GBR_performance_summary_df():
    """
    Load dataframe with models and performance data of Gradient Boosting Regression (GBR) models from analysis
    published in "Interpretable Machine Learning to Model Biomass and Waste Gasification"
    (https://doi.org/10.1016/j.biortech.2022.128062).

    Returns
    -------
    DataFrame

    """
    # Get file path to GBR data
    project_root = get_project_root()
    full_file_path = str(project_root) + r"\data\GBR_performance_summary"

    # Load performance summary object
    perf_summary = pickle.load(open(full_file_path, "rb"))

    return perf_summary
