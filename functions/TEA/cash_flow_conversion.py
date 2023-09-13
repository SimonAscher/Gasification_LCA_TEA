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

    if value_type == "FV":
        pv = value * (1 / (1 + interest_rate)) ** discount_period

    elif value_type == "AV":
        pv = value * ((((1 + interest_rate) ** discount_period) - 1) / (
                interest_rate * ((1 + interest_rate) ** discount_period)))
    else:
        raise ValueError(r"Warning: This type of reference value is not supported. Only 'FV' or 'AV' supported.")

    return pv


def get_annual_value(value, value_type, interest_rate=None, discount_period=None):
    """
    Convert present value or present value to annual value (also called annuity).

    Parameters
    ----------
    value : float
        Defines the original value given as its PV or FV.
    value_type: str
        Defines if the known value is the present value (PV) or future value (FV) (Options: 'PV' or 'FV').
    interest_rate: float
        Interest rate given as a decimal (e.g. 5 % should be entered as 0.05).
    discount_period: float
        Discount period given in years.

    Returns
    -------
    float
        Annual value (also called annuity) of imputed cost or benefit object
    """
    if interest_rate is None:
        interest_rate = settings.data.economic.interest_rate.year_2023[settings.user_inputs.general.currency]
    if discount_period is None:
        discount_period = settings.data.economic.system_lifecycle
    # TODO: Write some tests for this function - has not been tested yet.

    if value_type == "PV":
        av = value * (interest_rate*((1+interest_rate)**discount_period)/(((1+interest_rate)**discount_period)-1))

    elif value_type == "FV":
        av = value * (interest_rate/(((1+interest_rate)**discount_period)-1))
    else:
        raise ValueError(r"Warning: This type of reference value is not supported. Only 'PV' or 'FV' supported.")

    return av
