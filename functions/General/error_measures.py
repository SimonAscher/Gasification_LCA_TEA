import numpy as np
from numpy.typing import ArrayLike


def MAPE(y_true, y_pred, return_as_decimal=False):
    """
    Function to calculate mean absolute percentage error.
    Parameters
    ----------
    y_true: ArrayLike | list
        True values.
    y_pred: ArrayLike | list
        Predicted values.
    return_as_decimal: bool
        If False return output as percentage error; if True return output as decimal.

    Returns
    -------
    float
        Mean absolute percentage error in percent (or in decimal if return_as_decimal=True).
    """
    #
    error_values = np.abs((y_true - y_pred) / y_true) * 100
    error_values = np.asarray(error_values)
    # inf_mask = ~np.isfinite(error_values)  # check for values which are infinity due to division by zero
    # error_values[inf_mask == True] = 0 # can be used to avoid infinite values - however this is not really a valid assumption - as it would just assume perfect prediction accuracy for all the cases where the true value is zero
    mape = np.mean(error_values)

    if return_as_decimal:
        mape = mape / 100

    return mape
