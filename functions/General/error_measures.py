import numpy as np


def MAPE(y_true, y_pred):
    """
    Function to calculate mean absolute percentage error.
    Parameters
    ----------
    y_true
        True values.
    y_pred
        Predicted values.
    Returns
    -------
    float
        Mean absolute percentage error (in percent - not decimal).
    """
    #
    error_values = np.abs((y_true - y_pred) / y_true) * 100
    error_values = np.asarray(error_values)
    inf_mask = ~np.isfinite(error_values)  # check for values which are infinity due to division by zero
    # error_values[inf_mask == True] = 0 # can be used to avoid infinite values - however this is not really a valid assumption - as it would just assume perfect prediction accuracy for all the cases where the true value is zero
    mape = np.mean(error_values)

    return mape
