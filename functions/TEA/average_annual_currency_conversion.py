import datetime
import cachetools.func
import warnings

import numpy as np
import yfinance as yf

from forex_python.converter import CurrencyRates, RatesNotAvailableError


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
        end_date = datetime.datetime.today().date() - datetime.timedelta(14)  # use date 2 weeks prior to avoid bugs
        warnings.warn("Current year selected. Hence average up to 2 weeks prior used instead of complete annual "
                      "average. Consider running analysis based on last year's data instead.")

    return start_date, end_date


@cachetools.func.ttl_cache(maxsize=10, ttl=360)
def get_average_annual_exchange_rate(year, base_currency, converted_currency, approximate_rate=False, method=None):
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
    method: str
        Determines which method (or api) should be used to fetch exchange rates from.

    Returns
    -------
    float
        Average exchange rate for the given year.
    """
    # Get defaults
    if method is None:
        method = "yfinance"

    start_date, end_date = get_year_start_end_date(year)

    # Define methods as helper functions
    def run_with_forex_python():
        # Get parameters to iterate through year
        date_delta = datetime.timedelta(days=1)  # set increment by which date should be increased - i.e. 1 day
        date = start_date  # initiate date which is used for counting
        historic_rates_array = []
        currency_rates = CurrencyRates()
        exceptions_counter = 0
        none_values_counter = 0
        # Iterate over range of dates and get exchange rates
        while date <= end_date:
            date += date_delta
            if approximate_rate:
                date += datetime.timedelta(days=13)

            try:
                historic_rates_array.append(currency_rates.get_rate(base_cur=base_currency,
                                                                    dest_cur=converted_currency,
                                                                    date_obj=date))
            except RatesNotAvailableError:  # try next day if rate could not be fetched
                try:
                    exceptions_counter += 1
                    historic_rates_array.append(currency_rates.get_rate(base_cur=base_currency,
                                                                        dest_cur=converted_currency,
                                                                        date_obj=date + datetime.timedelta(days=1)))
                except RatesNotAvailableError:  # skip value if rate could not be fetched again
                    none_values_counter += 1

        # Raise error if too many exceptions occurred
        if approximate_rate:
            if none_values_counter > 3:
                raise RatesNotAvailableError("Exchange rate could not be fetched on too many instances.")
        else:
            if none_values_counter > 3 * 13:
                raise RatesNotAvailableError("Exchange rate could not be fetched on too many instances.")

        return historic_rates_array

    def run_with_yfinance():
        from functions.general.utility import HidePrints
        with HidePrints():
            # Get yahoo finance code and fetch data from api
            yahoo_finance_code = base_currency + converted_currency + "=X"
            historic_rates_array = list(yf.download(yahoo_finance_code, start=start_date, end=end_date).Close)

        return historic_rates_array

    # Run with appropriate method
    if method == "forex_python":
        try:
            historic_rates_array = run_with_forex_python()
        except:  # slower but sometimes yfinance breaks
            warnings.warn("Error with forex_python - revert to yfinance library")
            historic_rates_array = run_with_yfinance()


    elif method == "yfinance":
        try:
            historic_rates_array = run_with_yfinance()
        except:  # slower but sometimes yfinance breaks
            warnings.warn("Error with yfinance - revert to slower method using forex_python library")
            historic_rates_array = run_with_forex_python()
    else:
        raise ValueError("Method not supported.")

    historic_rates_array = float(np.mean(historic_rates_array))

    return historic_rates_array


def convert_currency_annual_average(value, year, base_currency, converted_currency, approximate_rate=False,
                                    method=None):
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
    method: str
        Determines which method (or api) should be used to fetch exchange rates from.
    Returns
    -------
    float
        Converted value in desired currency.
    """
    average_exchange_rate = get_average_annual_exchange_rate(year, base_currency, converted_currency, approximate_rate,
                                                             method)
    converted_value = average_exchange_rate * value

    return converted_value
