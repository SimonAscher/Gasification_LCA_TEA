import functools

from config import settings
from forex_python.converter import CurrencyRates
from datetime import datetime


def _convert_single_currency(base_currency, output_currency, amount, date_obj):
    """
    Converts a single currency value from a base currency to a desired currency.
    Expanded by convert_currency function to extend to list and numpy arrays.

    Parameters
    ----------
    base_currency: str
    output_currency: str
    amount : float | int
    date_obj: str | int

    Returns
    -------
    float
        Amount converted to output currency.
    """

    # Set up converter
    output_amount = None
    converter = CurrencyRates()
    if date_obj == "reference date":
        reference_date_time = datetime(*settings.data.economic.reference_date)
        output_amount = converter.convert(base_currency, output_currency, amount, reference_date_time)

    if date_obj == "most recent":
        output_amount = converter.convert(base_currency, output_currency, amount)

    if isinstance(date_obj, datetime):
        output_amount = converter.convert(base_currency, output_currency, amount, date_obj)

    if date_obj == 2022:  # uses annual averages
        annual_average_data = settings.data.economic.conversion_rates.year_2022

        if base_currency == "USD" and output_currency == "GBP":
            output_amount = amount * annual_average_data.USD_TO_GBP
        if base_currency == "USD" and output_currency == "EUR":
            output_amount = amount * annual_average_data.USD_TO_GBP * 1 / annual_average_data.EUR_TO_GBP
        if base_currency == "EUR" and output_currency == "GBP":
            output_amount = amount * annual_average_data.EUR_TO_GBP
        if base_currency == "EUR" and output_currency == "USD":
            output_amount = amount * annual_average_data.EUR_TO_GBP * 1 / annual_average_data.USD_TO_GBP
        if base_currency == "GBP" and output_currency == "USD":
            output_amount = amount * 1 / annual_average_data.USD_TO_GBP
        if base_currency == "GBP" and output_currency == "EUR":
            output_amount = amount * 1 / annual_average_data.EUR_TO_GBP

    return output_amount


def convert_currency(base_currency, output_currency, amounts, date_obj=2022):
    """
    Converts a value or a list (or "np.array") of values to another currency.
    Currency keys are: "GBP", "USD", "EUR".

    Parameters
    ----------
    base_currency: str
        Original currency.
    output_currency: str
        Desired currency post conversion.
    amounts : float | int | list[float] | list[int]
        Amount which is to be converted.
    date_obj: str | int | datetime
        Determines which reference date or timeframe should be used for conversion.

    Returns
    -------
    float| list[float]
        Amount converted to output currency.
    """

    if isinstance(amounts, int) or isinstance(amounts, float):  # single value case
        output_amount = _convert_single_currency(base_currency, output_currency, amounts, date_obj="reference date")
    else:  # list or other iterable of values case
        partial_function = functools.partial(_convert_single_currency, base_currency=base_currency,
                                             output_currency=output_currency, date_obj=date_obj)
        output_amount = [partial_function(amount=x) for x in amounts]

    return output_amount
