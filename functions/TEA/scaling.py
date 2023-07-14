import warnings

from config import settings


def power_scale(baseline_size, design_size, baseline_cost, scaling_factor=0.7):
    """
    Power scaling method used to scale the capital cost (CAPEX) of a designed plant based on the cost of a reference
    plant.

    Parameters
    ----------
    baseline_size: float
        Baseline size of plant in e.g. kW, tonnes per day, etc.
    design_size: float
        Size of designed plant - ensure same units used as for baseline_size.
    baseline_cost: float
        Baseline cost of plant.
    scaling_factor: float
        Scaling factor to be used in power scaling technique - also see note for more information.

    Returns
    -------
    float
        Plant capital cost after power scaling

    Notes
    -----
    Default scaling factor (f) is 0.7, other factors may be appropriate for certain scenarios
    (e.g. Angelonidi & Smith (2015) uses a more linear f closer to 1.0).
    """

    scaled_cost = baseline_cost * ((design_size / baseline_size) ** scaling_factor)

    return scaled_cost


def get_most_recent_available_CEPCI_year():
    """
    Helper function to be used with CEPCI_scale.
    Checks for most recent CEPCI value stored in database and returns corresponding year.

    Returns
    -------

    """
    CEPCI_values = dict(settings.data.economic.CEPCI)
    CEPCI_values.pop("source")

    count = 0
    while True:
        dict_key = str(int(max(CEPCI_values)) - count)
        count += 1
        dict_value = CEPCI_values[dict_key]
        if dict_value != "unavailable":
            break

    return int(dict_key)


def CEPCI_scale(base_year, design_year, value):
    """
    Converts a value from a base year to a design year using the Chemical Engineering Plant Cost Index (CEPCI).

    Parameters
    ----------
    base_year: int
        Base or reference year of the system.
    design_year: int
        Year the system is supposed to be updated to.
    value: float | int
        Value of the reference or base year.

    Returns
    -------
    float
        CEPCI scaled value.
    """

    # Get CEPCI values
    CEPCI_data = settings.data.economic.CEPCI
    design_CEPCI = CEPCI_data[str(design_year)]
    base_CEPCI = CEPCI_data[str(base_year)]

    # Raise Error/Warning if CEPCI value unavailable.
    if base_CEPCI == "unavailable":
        raise ValueError("CEPCI value not available for base year.")

    if design_CEPCI == "unavailable":
        design_CEPCI = CEPCI_data[str(get_most_recent_available_CEPCI_year())]
        warnings.warn("CEPCI value not available for design year. Reverted to most recent CEPCI value.")

    # Convert value
    scaled_value = value * (design_CEPCI / base_CEPCI)

    return scaled_value
