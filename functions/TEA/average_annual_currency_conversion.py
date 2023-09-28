import datetime
import cachetools.func
import warnings

import numpy as np

from forex_python.converter import CurrencyRates


def get_year_start_end_date(year):
    """
    Gets the first and last day of a given year in datetime format.
    Helper function for get_average_annual_exchange_rate.

    Parameters
    ----------
    year: int
        The year of interest.

    Returns
    -------
    tuple[datetime.datetime, datetime.datetime]
        The start and end date of the year.

    """
    start_date = datetime.datetime(year=year, month=1, day=1).date()
    end_date = datetime.datetime(year=year, month=12, day=31).date()

    if year == datetime.datetime.today().year:
        end_date = datetime.datetime.today().date() - datetime.timedelta(1)  # use yesterday's date to avoid bugs
        warnings.warn("Current year selected. Hence average up to yesterday used instead of complete annual average. "
                      "Consider running analysis based on last year's data instead.")

    return start_date, end_date


@cachetools.func.ttl_cache(maxsize=10, ttl=360)
def get_average_annual_exchange_rate(year, base_currency, converted_currency, approximate_rate=False):
    """
    Gets the average annual exchange rate for a given year.

    Parameters
    ----------
    year: int
        The year of interest.
    base_currency: str
        String indicating the base currency.
    converted_currency: str
        String indicating the currency which to convert to.
    approximate_rate: bool
        Calculates the approximate average exchange rate for a given year instead (only takes 1 values every 2 weeks).
        This significantly speeds up the calculations but may be less accurate.

    Returns
    -------
    float
        Average exchange rate for the given year.
    """
    # Get parameters to iterate through year
    start_date, end_date = get_year_start_end_date(year)
    date_delta = datetime.timedelta(days=1)  # set increment by which date should be increased - i.e. 1 day
    date = start_date  # initiate date which is used for counting
    historic_rates_array = []
    currency_rates = CurrencyRates()

    # Iterate over range of dates and get exchange rates
    while date <= end_date:
        date += date_delta
        if approximate_rate:
            date += datetime.timedelta(days=13)
        historic_rates_array.append(currency_rates.get_rate(base_cur=base_currency,
                                                            dest_cur=converted_currency,
                                                            date_obj=date))
    historic_rates_array = np.mean(historic_rates_array)

    return historic_rates_array


def convert_currency_annual_average(value, year, base_currency, converted_currency, approximate_rate=False):
    """
    Converts a value from an original currency to a new currency for a given year.

    Parameters
    ----------
    value: float
        Value to be converted from base currency to desired currency.
    year: int
        The year of interest.
    base_currency: str
        String indicating the base currency.
    converted_currency: str
        String indicating the currency which to convert to.
    approximate_rate: bool
        Calculates the approximate average exchange rate for a given year instead (only takes 1 values every 2 weeks).
        This significantly speeds up the calculations but may be less accurate.

    Returns
    -------
    float
        Converted value in desired currency.
    """
    average_exchange_rate = get_average_annual_exchange_rate(year, base_currency, converted_currency, approximate_rate)
    converted_value = average_exchange_rate * value

    return converted_value
