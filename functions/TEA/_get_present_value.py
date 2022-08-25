def get_present_value(value: float, value_type: str, interest_rate: float = 0.05, discount_period: int = 20) -> float:
    """
    Convert future value or annual value to present value.

    Parameters
    ----------
    value : float
        Defines the reference value given as its FV or AV
    value_type: str
        Defines if the known value is the future value (FV) or annual value (AV) (Options: 'FV' or 'AV')
    interest_rate: float
        Interest rate given as a decimal (e.g. 5 % should be entered as 0.05)
    discount_period: float
        Discount period given in years

    Returns
    -------
    float
        Present value of imputed cost or benefit object
    """

    # TODO: Update default interest rate and discount period at later stage if necessary - put these in settings files

    pv = []
    if value_type == "FV":
        pv = value * (1 / (1 + interest_rate)) ** discount_period

    elif value_type == "AV":
        pv = value * ((((1 + interest_rate) ** discount_period) - 1) / (
                interest_rate * ((1 + interest_rate) ** discount_period)))
    else:
        print('Warning: This type of reference value is not supported!')
        # TODO: Turn this warning statement into a proper warning
    return pv
