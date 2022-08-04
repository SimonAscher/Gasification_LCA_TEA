import numpy as np


def scale_gas_fractions(gas_fractions):
    """
    Scales gas fractions, so they sum up to 100 %.

    Parameters
    ----------
    gas_fractions: array[float]
        Array of gas fractions which are to be scaled
    Returns
    -------
    array[float]
        Array of scaled gas fractions

    """
    
    # Set up empty list to store scaled values
    unscaled_total = sum(gas_fractions)
    scaled_gas_fractions = np.array(gas_fractions * 100 / unscaled_total)

    return scaled_gas_fractions
