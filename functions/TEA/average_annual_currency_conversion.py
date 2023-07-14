import datetime
import cachetools.func
import requests
import warnings

import numpy as np
# import time


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
def get_average_annual_exchange_rate(year, base_currency, converted_currency):
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

    Returns
    -------
    float
        Average exchange rate for the given year.
    """
    # Inspired by Indently on Youtube (https://www.youtube.com/watch?v=dCUb1tky1-Q)

    # start_time = time.time()

    # Get start and end date of year
    start_date, end_date = get_year_start_end_date(year)

    # Get data from api
    url = f"https://api.exchangerate.host/timeseries"
    url_params = {"base": base_currency, "start_date": start_date, "end_date": end_date}
    url_response = requests.get(url, url_params)
    url_data = url_response.json()
    # TODO: Consider storing data in a database etc. to speed things up and avoid url request every time function is run

    # Store data in array
    rate_history_array = []

    for item in url_data["rates"]:
        currency_rate = url_data["rates"][item][converted_currency]
        rate_history_array.append(currency_rate)

    rate_history_average = np.mean(rate_history_array)
    # end_time = time.time()
    # print(end_time-start_time)

    return rate_history_average


def convert_currency_annual_average(value, year, base_currency, converted_currency):
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

    Returns
    -------
    float
        Converted value in desired currency.
    """
    average_exchange_rate = get_average_annual_exchange_rate(year, base_currency, converted_currency)
    converted_value = average_exchange_rate * value

    return converted_value
