import os
import functions

import pandas as pd
import numpy as np

from config import settings
from objects import PresentValue, triangular_dist_maker
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error


def get_boiler_CAPEX_distribution(unit_steam_requirement, currency=None, CEPCI_year=None):
    """
    Calculate the CAPEX distribution of a boiler for steam generation.
    CAPEX is given as total overnight cost (TOC) or total installed cost (TIC) (i.e. engineering works, procurement,
    installation, etc. are considered included in CAPEX).

    Parameters
    ----------
    unit_steam_requirement: float
        Steam requirement [kg steam/kg feedstock wb].
    currency: str | None
        Currency that is to be used for analysis.
    CEPCI_year: int | None
        Reference CEPCI year that is to be used for analysis.

    Returns
    -------
    PresentValue
        Present value object containing distribution of CAPEX values in the supplied currency.
    """

    # Get default inputs
    if currency is None:
        currency = settings.user_inputs.general.currency

    if CEPCI_year is None:
        CEPCI_year = settings.user_inputs.economic.CEPCI_year

    # Get system size
    system_size_tonnes_per_hour = settings.user_inputs.system_size.mass_basis_tonnes_per_hour  # [tonnes/hour]
    unit_steam_requirement *= 1000  # update to [kg steam/tonne feedstock wb]
    steam_requirement = unit_steam_requirement * system_size_tonnes_per_hour  # [kg steam/hour]

    # Load data
    root_dir = functions.general.utility.get_project_root()
    data_file = "CAPEX_boiler.csv"
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

    # Discard outliers
    df = df[df["CAPEX"] < 500000]

    # Fit model, get error metrics, and prediction.
    popt, _ = curve_fit(f=functions.general.curve_fitting.func_straight_line,
                        xdata=df["Plant size [kg steam/hour]"],
                        ydata=df[currency_and_CEPCI_scaled_label],
                        maxfev=10000)

    mape_decimal = functions.general.MAPE(df[currency_and_CEPCI_scaled_label],
                                          functions.general.curve_fitting.func_straight_line(
                                              df["Plant size [kg steam/hour]"], *popt),
                                          return_as_decimal=True)

    prediction = functions.general.curve_fitting.func_straight_line(steam_requirement, *popt)

    if steam_requirement < 2000:
        # Overwrite prediction if system is very small scale - use power scaling approach instead
        smallest_system_data = (df[df["Plant size [kg steam/hour]"] == df["Plant size [kg steam/hour]"].min()])
        smallest_system_cost = smallest_system_data[currency_and_CEPCI_scaled_label]
        smallest_system_size = smallest_system_data["Plant size [kg steam/hour]"]

        prediction = float(functions.TEA.power_scale(baseline_size=float(smallest_system_size),
                                                     design_size=steam_requirement,
                                                     baseline_cost=float(smallest_system_cost),
                                                     scaling_factor=0.8))
        mape_decimal = 0.30  # Add significant uncertainty to model - since reliant on individual data point here.

    # Get lower and upper bounds of distribution based on the distributions MAPE
    lower_bound = prediction - (prediction * mape_decimal)
    upper_bound = prediction + (prediction * mape_decimal)

    distribution = triangular_dist_maker(lower=lower_bound, mode=prediction, upper=upper_bound)

    distribution_draws = list(np.multiply(
        functions.MonteCarloSimulation.get_distribution_draws(distribution), -1))  # turn -ve as they are a cost

    CAPEX = PresentValue(values=distribution_draws,
                         name="CAPEX Boiler for Steam Generation",
                         short_label="CAPEX Stm",
                         tag="CAPEX")

    return CAPEX
