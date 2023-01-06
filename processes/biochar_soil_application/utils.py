import pickle


def load_biochar_properties_data(full_file_path=r"C:\Users\2270577A\PycharmProjects\PhD_LCA_TEA\data"
                                               r"\biochar_properties_results"):
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
    # Load pickled data
    loaded_data = pickle.load(open(full_file_path, "rb"))
    # TODO: Change call to file path to dynamic call (could try something like sys.path[-1])

    return loaded_data
