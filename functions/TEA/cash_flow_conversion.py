import functools
import inspect

from config import settings
from typing import Literal

_value_type_options_pv = Literal["AV", "FV"]
_value_type_options_av = Literal["PV", "FV"]


def check_args_for_percentage(*args):
    """
    Decorator which checks if given keyword arguments are given as decimals.
    """

    def decorator(func):
        func_args_by_name = inspect.getfullargspec(func).args
        indices_of_args = [func_args_by_name.index(arg) for arg in args]

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            for n in indices_of_args:
                assert args[n] <= 1, f"Error in function argument number {n}. Should be decimal."

            return func(*args, **kwargs)

        return wrapped

    return decorator


# @check_args_for_percentage("interest_rate")
def get_present_value(values, value_type: _value_type_options_pv, interest_rate=None, discount_period=None):
    """
    Convert future value or annual value to present value.

    Parameters
    ----------
    values : float | int | list[float] | list[int]
        Defines the original values given as its FV or AV.
    value_type: str
        Defines if the known values are given as annual value (AV) or future value (FV).
    interest_rate: float | int
        Interest rate given as a decimal (e.g. 5 % should be entered as 0.05).
    discount_period: float | int
        Discount period given in years.

    Returns
    -------
    float | list[float]
        Present value of imputed cost or benefit object
    """

    # Helper function for single value
    def _get_single_present_value(_value, _value_type: _value_type_options_pv, _interest_rate=None,
                                  _discount_period=None):
        """
        Convert future value or annual value to present value.
        Expanded by get_present_value function to extend to list and numpy arrays.

        Parameters
        ----------
        _value : float | int
            Defines the original value given as its FV or AV.
        _value_type: str
            Defines if the known value is the annual value (AV) or future value (FV).
        _interest_rate: float | int
            Interest rate given as a decimal (e.g. 5 % should be entered as 0.05).
        _discount_period: float | int
            Discount period given in years.

        Returns
        -------
        float
            Present value of imputed cost or benefit object
        """
        if _interest_rate is None:
            _interest_rate = settings.data.economic.interest_rate.year_2023[settings.user_inputs.general.currency]
        if _discount_period is None:
            _discount_period = settings.data.economic.system_lifecycle

        if _value_type == "FV":
            _pv = _value / ((1 + _interest_rate) ** _discount_period)

        elif _value_type == "AV":
            _pv = _value * ((((1 + _interest_rate) ** _discount_period) - 1) / (
                    _interest_rate * ((1 + _interest_rate) ** _discount_period)))
        else:
            raise ValueError(r"Warning: This type of reference value is not supported. Only 'FV' or 'AV' supported.")

        # Run check
        if _interest_rate > 1:
            raise ValueError("Interest rate should be given as a decimal.")

        return _pv

    # Extension of inner function to lists and numpy arrays if required.
    if isinstance(values, int) or isinstance(values, float):  # single value case
        pv = _get_single_present_value(values, value_type, interest_rate, discount_period)
    else:  # list or other iterable of values case
        partial_function = functools.partial(_get_single_present_value,
                                             _value_type=value_type,
                                             _interest_rate=interest_rate,
                                             _discount_period=discount_period)
        pv = [partial_function(_value=x) for x in values]

    return pv


# @check_args_for_percentage("interest_rate")
def get_annual_value(values, value_type: _value_type_options_av, interest_rate=None, discount_period=None):
    """
    Convert present values or future values to annual values (also called annuity).

    Parameters
    ----------
    values : float | int | list[float] | list[int]
        Defines the original values given as its PV or FV.
    value_type: str
        Defines if the known values are given as present value (PV) or future value (FV).
    interest_rate: float | int
        Interest rate given as a decimal (e.g. 5 % should be entered as 0.05).
    discount_period: float | int
        Discount period given in years.

    Returns
    -------
    float | list[float]
        Annual value (also called annuity) of imputed cost or benefit object
    """

    def _get_single_annual_value(_value, _value_type: _value_type_options_av, _interest_rate=None,
                                 _discount_period=None):
        """
        Convert present value or present value to annual value (also called annuity).

        Parameters
        ----------
        _value : float | int
            Defines the original value given as its PV or FV.
        _value_type: str
            Defines if the known value is the present value (PV) or future value (FV).
        _interest_rate: float | int
            Interest rate given as a decimal (e.g. 5 % should be entered as 0.05).
        _discount_period: float | int
            Discount period given in years.

        Returns
        -------
        float
            Annual value (also called annuity) of imputed cost or benefit object
        """
        if _interest_rate is None:
            _interest_rate = settings.data.economic.interest_rate.year_2023[settings.user_inputs.general.currency]
        if _discount_period is None:
            _discount_period = settings.data.economic.system_lifecycle

        if _value_type == "PV":
            _av = _value * ((_interest_rate * ((1 + _interest_rate) ** _discount_period)) / (
                        ((1 + _interest_rate) ** _discount_period) - 1))

        elif _value_type == "FV":
            _av = _value * (_interest_rate / (((1 + _interest_rate) ** _discount_period) - 1))
        else:
            raise ValueError(r"Warning: This type of reference value is not supported. Only 'PV' or 'FV' supported.")

        # Run check
        if _interest_rate > 1:
            raise ValueError("Interest rate should be given as a decimal.")

        return _av

    # Extension of inner function to lists and numpy arrays if required.
    if isinstance(values, int) or isinstance(values, float):  # single value case
        av = _get_single_annual_value(values, value_type, interest_rate, discount_period)
    else:  # list or other iterable of values case
        partial_function = functools.partial(_get_single_annual_value,
                                             _value_type=value_type,
                                             _interest_rate=interest_rate,
                                             _discount_period=discount_period)
        av = [partial_function(_value=x) for x in values]

    return av
