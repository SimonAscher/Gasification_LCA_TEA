import numpy as np


def reject_outliers(data, std_cut_off=3):
    """
    Reject outliers from a numpy array.


    Parameters
    ----------
    data: np.array
        Input data containing potential outliers.
    std_cut_off: int
        Defines cut-off based on number of standard deviations from the mean (e.g. 2 - 95% and 3 - 99.7%).


    Returns
    -------
    np.array
        Data without outliers
    """
    return data[abs(data - np.mean(data)) < std_cut_off * np.std(data)]
