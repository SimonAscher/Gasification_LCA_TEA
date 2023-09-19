# Simple functions to convert between different units

# Energy units

def kJ_to_kWh(value, reverse=False):
    """
    Convert from kJ to kWh (or reverse if reverse=True).

    Parameters
    ----------
    value: float | int
        Value which is to be converted.
    reverse: bool
        Determines whether conversion should be done reversed.

    Returns
    -------
    Converted value in kWh (or kJ if reverse=True).
    """
    value_out = value / 3600
    if reverse:
        value_out = 3600 * value

    return value_out


def MJ_to_kWh(value, reverse=False):
    """
    Convert from MJ to kWh (or reverse if reverse=True).

    Parameters
    ----------
    value: float | int
        Value which is to be converted.
    reverse: bool
        Determines whether conversion should be done reversed.

    Returns
    -------
    Converted value in kWh (or MJ if reverse=True).
    """
    value_out = value / 3.6
    if reverse:
        value_out = 3.6 * value

    return value_out


def therm_to_kWh(value, reverse=False):
    """
    Converts therms (thm) (e.g 1 thm = 100,000 BTU = 29.3 kWh) to their kWh equivalent.

    Parameters
    ----------
    value
    reverse

    Returns
    -------

    """
    value_out = 29.3072 * value
    if reverse:
        value_out = value / 29.3072

    return value_out
