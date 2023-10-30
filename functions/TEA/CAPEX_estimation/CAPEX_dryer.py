import os
import functions

import pandas as pd
import numpy as np

from config import settings
from objects import PresentValue, triangular_dist_maker
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error


def get_dryer_CAPEX_distribution(currency=None, CEPCI_year=None):
    """
    Calculate the CAPEX distribution of a dryer for feedstock drying.
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
        Present value object containing distribution of CAPEX values in the supplied currency.
    """

    # Get default inputs
    if currency is None:
        currency = settings.user_inputs.general.currency

    if CEPCI_year is None:
        CEPCI_year = settings.user_inputs.economic.CEPCI_year

    # Calculate system size in terms of kg H2O removed/hour.
    # Get background data
    mass_feedstock = settings.general.FU  # i.e. 1000 kg
    moisture_ar = settings.user_inputs.feedstock.moisture_ar
    moisture_post_drying = settings.user_inputs.feedstock.moisture_post_drying

    # Check for erroneous inputs
    if moisture_ar < 1 or moisture_post_drying < 1:
        raise ValueError("Ensure that moisture contents are given as percentages.")
    if moisture_ar < moisture_post_drying:
        raise ValueError("Warning: Moisture content of as received feedstock must be higher than moisture content "
                         "post drying.")

    # Turn moisture's from percentages to decimals
    moisture_ar /= 100
    moisture_post_drying /= 100

    # Calculate mass of evaporated water:
    mass_water_initial = mass_feedstock * moisture_ar
    mass_feed_dry = mass_feedstock * (1 - moisture_ar)
    mass_water_post_drying = (mass_feed_dry * moisture_post_drying) / (1 - moisture_post_drying)
    mass_evaporated_water_per_FU = mass_water_initial - mass_water_post_drying  # [kg/FU]

    # Get final system size
    system_size_tonnes_per_hour = settings.user_inputs.system_size.mass_basis_tonnes_per_hour  # [tonnes/hour]
    system_size_kg_H2O_per_hour = mass_evaporated_water_per_FU * system_size_tonnes_per_hour  # [kg H2O/hour]

    # Load data
    root_dir = functions.general.utility.get_project_root()
    data_file = "CAPEX_dryer.csv"
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

    # Select data to fit model based on system's size
    if system_size_kg_H2O_per_hour < 1000:  # size < 1,000
        df = df[df["Ignore"] != True].copy()
        df = df[df["Plant size [kg H2O/hour]"] < 1000]
        df = df.dropna(subset=['CAPEX_GBP_CEPCI_2020'])
    elif system_size_kg_H2O_per_hour < 10000:  # size 1,000 to 10,000
        df = df[df["Ignore"] != True].copy()
        df = df[df["Plant size [kg H2O/hour]"].between(1000, 10000)]
        df = df[df["Reference_label"] == "g"]
        df = df.dropna(subset=['CAPEX_GBP_CEPCI_2020'])
    else:  # size >10,000
        df = df[df["Ignore"] != True].copy()
        df = df[df["Plant size [kg H2O/hour]"].between(1000, 30000)]
        df = df.dropna(subset=['CAPEX_GBP_CEPCI_2020'])
    # Fit model, get error metrics, and prediction.
    popt, _ = curve_fit(f=functions.general.curve_fitting.func_straight_line,
                        xdata=df["Plant size [kg H2O/hour]"],
                        ydata=df[currency_and_CEPCI_scaled_label],
                        maxfev=10000)

    mape_decimal = functions.general.MAPE(df[currency_and_CEPCI_scaled_label],
                                          functions.general.curve_fitting.func_straight_line(
                                              df["Plant size [kg H2O/hour]"], *popt),
                                          return_as_decimal=True)

    prediction = functions.general.curve_fitting.func_straight_line(system_size_kg_H2O_per_hour, *popt)

    # Get lower and upper bounds of distribution based on the distributions MAPE
    lower_bound = prediction - (prediction * mape_decimal)
    upper_bound = prediction + (prediction * mape_decimal)

    distribution = triangular_dist_maker(lower=lower_bound, mode=prediction, upper=upper_bound)

    distribution_draws = list(np.multiply(
        functions.MonteCarloSimulation.get_distribution_draws(distribution), -1))  # turn -ve as they are a cost

    CAPEX = PresentValue(values=distribution_draws,
                         name="CAPEX Feedstock Dryer",
                         short_label="CAPEX Dry",
                         tag="CAPEX")

    return CAPEX
