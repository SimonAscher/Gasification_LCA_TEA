import os

from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error

import functions

import pandas as pd
import numpy as np

from config import settings
from objects import PresentValue, triangular_dist_maker


def get_milling_CAPEX_distribution(currency=None, CEPCI_year=None):
    """
    Calculate the CAPEX distribution of a feedstock mill to reduce the particle size of a feedstock.
    CAPEX is given as total overnight cost (TOC) or total installed cost (TIC) (i.e. engineering works, procurement,
    installation, etc. are considered included in CAPEX).

    Parameters
    ----------
    currency: str | None
        Currency that is to be used for analysis.
    CEPCI_year: int | None
        Reference CEPCI year that is to be used for analysis.

    Returns
    -------
    PresentValue
        Distribution of CAPEX values in the supplied currency.

    """
    # Get defaults
    if currency is None:
        currency = settings.user_inputs.general.currency

    if CEPCI_year is None:
        CEPCI_year = settings.user_inputs.economic.CEPCI_year

    # Get system size
    system_size_tonnes_per_hour = settings.user_inputs.system_size.mass_basis_tonnes_per_hour

    # Load data
    root_dir = functions.general.utility.get_project_root()
    data_file = "CAPEX_hammermill.csv"
    data_file_path = os.path.join(root_dir, "data", data_file)
    df = pd.read_csv(data_file_path)

    # Convert all values to same currency and update to most recent CEPCI value
    CAPEX_currency_scaled = []
    CAPEX_currency_CEPCI_scaled = []

    for row_no in df.index:
        CAPEX_currency_scaled.append(functions.TEA.convert_currency_annual_average(value=df["CAPEX"][row_no],
                                                                                   year=df["Reference Year"][row_no],
                                                                                   base_currency=df["Currency"][row_no],
                                                                                   converted_currency=currency,
                                                                                   approximate_rate=False,
                                                                                   method="yfinance")
                                     )
        CAPEX_currency_CEPCI_scaled.append(functions.TEA.CEPCI_scale(base_year=df["Reference Year"][row_no],
                                                                     design_year=CEPCI_year,
                                                                     value=CAPEX_currency_scaled[row_no]))

    # Add (i) currency and (ii) currency + CEPCI scaled values to dataframe
    currency_scaled_label = "CAPEX_" + currency
    currency_and_CEPCI_scaled_label = "CAPEX_" + currency + "_CEPCI_" + str(CEPCI_year)
    df[currency_scaled_label] = CAPEX_currency_scaled
    df[currency_and_CEPCI_scaled_label] = CAPEX_currency_CEPCI_scaled

    # Remove data points which should be ignored
    df = df[df["Ignore"] != True].copy()

    # Fit model, get error metrics, and prediction.
    popt, _ = curve_fit(f=functions.general.curve_fitting.func_straight_line,
                        xdata=df["Plant size [tonnes/hour]"],
                        ydata=df[currency_and_CEPCI_scaled_label],
                        maxfev=10000)

    # rmse = mean_squared_error(df[currency_and_CEPCI_scaled_label],
    #                           functions.general.curve_fitting.func_straight_line(df["Plant size [tonnes/hour]"],
    #                                                                              *popt),
    #                           squared=False)

    mape_decimal = functions.general.MAPE(df[currency_and_CEPCI_scaled_label],
                                          functions.general.curve_fitting.func_straight_line(
                                              df["Plant size [tonnes/hour]"], *popt),
                                          return_as_decimal=True)

    prediction = functions.general.curve_fitting.func_straight_line(system_size_tonnes_per_hour, *popt)

    # Get lower and upper bounds of distribution based on the distributions MAPE
    lower_bound = prediction - (prediction * mape_decimal)
    upper_bound = prediction + (prediction * mape_decimal)

    distribution = triangular_dist_maker(lower=lower_bound, mode=prediction, upper=upper_bound)

    distribution_draws = list(np.multiply(functions.MonteCarloSimulation.get_distribution_draws(distribution), -1))  # turn -ve as they are a cost

    CAPEX = PresentValue(values=distribution_draws,
                         name="CAPEX Feedstock Mill",
                         short_label="CAPEX Mill")

    # TODO: Incorporate this
    """
    operation_and_maintenance_cost = 10% to 18%
    sources:
    "Development of agri-pellet production cost and optimum size", Sultana et al., 2010
    "Economics of producing fuel pellets from biomass", Mani et al., 2006
    life span of 10 years
    """

    return CAPEX


