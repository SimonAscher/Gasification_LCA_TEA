import pickle

from functions.general.utility import get_project_root


def load_biochar_properties_data(full_file_path=None):
    """
    Load pickled data done in analysis on biochar properties (e.g. carbon fraction and carbon stability)
    Analysis done in: analysis/preliminary/biochar_properties/biochar_properties.ipynb.

    Parameters
    ----------
    full_file_path: str
    "r" string specifying the file path to pickle object.

    Returns
    -------
    dict
        Loaded data on biochar properties.
    """
    if full_file_path is None:
        project_root = get_project_root()
        full_file_path = str(project_root) + r"\data\biochar_properties_results"

    # Load pickled data
    loaded_data = pickle.load(open(full_file_path, "rb"))

    return loaded_data
