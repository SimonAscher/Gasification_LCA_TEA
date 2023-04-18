from config import settings


def get_present_value(value, value_type, interest_rate=None, discount_period=None):
    """
    Convert future value or annual value to present value.

    Parameters
    ----------
    value : float
        Defines the original value given as its FV or AV.
    value_type: str
        Defines if the known value is the future value (FV) or annual value (AV) (Options: 'FV' or 'AV').
    interest_rate: float
        Interest rate given as a decimal (e.g. 5 % should be entered as 0.05).
    discount_period: float
        Discount period given in years.

    Returns
    -------
    float
        Present value of imputed cost or benefit object
    """
    if interest_rate is None:
        interest_rate = settings.data.economic.interest_rate.year_2023[settings.user_inputs.general.currency]
    if discount_period is None:
        discount_period = settings.data.economic.system_lifecycle

    pv = []
    if value_type == "FV":
        pv = value * (1 / (1 + interest_rate)) ** discount_period

    elif value_type == "AV":
        pv = value * ((((1 + interest_rate) ** discount_period) - 1) / (
                interest_rate * ((1 + interest_rate) ** discount_period)))
    else:
        raise ValueError(r"Warning: This type of reference value is not supported. Only 'FV' or 'AV' supported.")

    return pv
