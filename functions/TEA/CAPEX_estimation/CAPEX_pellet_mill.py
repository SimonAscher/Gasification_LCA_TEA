import os
import functions

import pandas as pd
import numpy as np

from config import settings
from objects import PresentValue, triangular_dist_maker
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error



def get_pellet_mill_and_cooler_CAPEX_distribution(currency=None, CEPCI_year=None):
    """
    Calculate the CAPEX distribution of a pellet mill and cooler to produce pellets for gasification.
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

    # Load data for pellet mill and cooler
    root_dir = functions.general.utility.get_project_root()

    # Mill
    data_file_pellet_mill = "CAPEX_pellet_mill.csv"
    data_file_path_pellet_mill = os.path.join(root_dir, "data", data_file_pellet_mill)
    df_pellet_mill = pd.read_csv(data_file_path_pellet_mill)

    # Cooler
    data_file_pellet_cooler = "CAPEX_pellet_cooler.csv"
    data_file_path_pellet_cooler = os.path.join(root_dir, "data", data_file_pellet_cooler)
    df_pellet_cooler = pd.read_csv(data_file_path_pellet_cooler)

    # Convert all values to same currency and update to most recent CEPCI value
    # Mill
    CAPEX_currency_scaled_mill = []
    CAPEX_currency_CEPCI_scaled_mill = []

    for row_no in df_pellet_mill.index:
        CAPEX_currency_scaled_mill.append(
            functions.TEA.convert_currency_annual_average(value=df_pellet_mill["CAPEX"][row_no],
                                                          year=df_pellet_mill["Reference Year"][row_no],
                                                          base_currency=df_pellet_mill["Currency"][row_no],
                                                          converted_currency=currency,
                                                          approximate_rate=False,
                                                          method="yfinance"))
        CAPEX_currency_CEPCI_scaled_mill.append(
            functions.TEA.CEPCI_scale(base_year=df_pellet_mill["Reference Year"][row_no],
                                      design_year=CEPCI_year,
                                      value=CAPEX_currency_scaled_mill[row_no]))

    # Add (i) currency and (ii) currency + CEPCI scaled values to dataframe
    currency_scaled_label = "CAPEX_" + currency
    currency_and_CEPCI_scaled_label = "CAPEX_" + currency + "_CEPCI_" + str(CEPCI_year)
    df_pellet_mill[currency_scaled_label] = CAPEX_currency_scaled_mill
    df_pellet_mill[currency_and_CEPCI_scaled_label] = CAPEX_currency_CEPCI_scaled_mill

    # Cooler
    CAPEX_currency_scaled_cooler = []
    CAPEX_currency_CEPCI_scaled_cooler = []

    for row_no in df_pellet_cooler.index:
        CAPEX_currency_scaled_cooler.append(
            functions.TEA.convert_currency_annual_average(value=df_pellet_cooler["CAPEX"][row_no],
                                                          year=df_pellet_cooler["Reference Year"][row_no],
                                                          base_currency=df_pellet_cooler["Currency"][row_no],
                                                          converted_currency=currency,
                                                          approximate_rate=False,
                                                          method="yfinance"))
        CAPEX_currency_CEPCI_scaled_cooler.append(
            functions.TEA.CEPCI_scale(base_year=df_pellet_cooler["Reference Year"][row_no],
                                      design_year=CEPCI_year,
                                      value=CAPEX_currency_scaled_cooler[row_no]))

    # Add (i) currency and (ii) currency + CEPCI scaled values to dataframe
    currency_scaled_label = "CAPEX_" + currency
    currency_and_CEPCI_scaled_label = "CAPEX_" + currency + "_CEPCI_" + str(CEPCI_year)
    df_pellet_cooler[currency_scaled_label] = CAPEX_currency_scaled_cooler
    df_pellet_cooler[currency_and_CEPCI_scaled_label] = CAPEX_currency_CEPCI_scaled_cooler

    # Fit models, get error metrics, and predictions.
    # Mill
    df_pellet_mill = df_pellet_mill[df_pellet_mill["doi"] != "10.2174/1876387101003010001"].copy()  # Discard outliers

    popt_mill, _ = curve_fit(f=functions.general.curve_fitting.func_straight_line,
                             xdata=df_pellet_mill["Plant size [tonnes/hour]"],
                             ydata=df_pellet_mill[currency_and_CEPCI_scaled_label],
                             maxfev=10000)

    mape_decimal_mill = functions.general.MAPE(df_pellet_mill[currency_and_CEPCI_scaled_label],
                                               functions.general.curve_fitting.func_straight_line(
                                                   df_pellet_mill["Plant size [tonnes/hour]"], *popt_mill),
                                               return_as_decimal=True)

    prediction_mill = functions.general.curve_fitting.func_straight_line(system_size_tonnes_per_hour, *popt_mill)

    # Get lower and upper bounds of distribution based on the distributions MAPE
    lower_bound_mill = prediction_mill - (prediction_mill * mape_decimal_mill)
    upper_bound_mill = prediction_mill + (prediction_mill * mape_decimal_mill)

    distribution_mill = triangular_dist_maker(lower=lower_bound_mill, mode=prediction_mill, upper=upper_bound_mill)

    distribution_draws_mill = list(np.multiply(
        functions.MonteCarloSimulation.get_distribution_draws(distribution_mill), -1))  # turn -ve as they are a cost

    CAPEX_mill = PresentValue(values=distribution_draws_mill,
                              name="CAPEX Pellet Mill",
                              short_label="CAPEX Pel_M",
                              tag="CAPEX",
                              number_of_periods=10)   # "Economics of producing fuel pellets from biomass", Mani et al., 2006

    # Cooler
    df_pellet_cooler = df_pellet_cooler[df_pellet_cooler["Reference Label"] != "b"]  # Discard outliers

    popt_cooler, _ = curve_fit(f=functions.general.curve_fitting.func_straight_line,
                               xdata=df_pellet_cooler["Plant size [tonnes/hour]"],
                               ydata=df_pellet_cooler[currency_and_CEPCI_scaled_label],
                               maxfev=10000)

    mape_decimal_cooler = functions.general.MAPE(df_pellet_cooler[currency_and_CEPCI_scaled_label],
                                                 functions.general.curve_fitting.func_straight_line(
                                                   df_pellet_cooler["Plant size [tonnes/hour]"], *popt_cooler),
                                                 return_as_decimal=True)

    prediction_cooler = functions.general.curve_fitting.func_straight_line(system_size_tonnes_per_hour, *popt_cooler)

    # Get lower and upper bounds of distribution based on the distributions MAPE
    lower_bound_cooler = prediction_cooler - (prediction_cooler * mape_decimal_cooler)
    upper_bound_cooler = prediction_cooler + (prediction_cooler * mape_decimal_cooler)

    distribution_cooler = triangular_dist_maker(lower=lower_bound_cooler,
                                                mode=prediction_cooler,
                                                upper=upper_bound_cooler)

    distribution_draws_cooler = list(np.multiply(
        functions.MonteCarloSimulation.get_distribution_draws(distribution_cooler), -1))  # turn -ve as they are a cost

    CAPEX_cooler = PresentValue(values=distribution_draws_cooler,
                                name="CAPEX Pellet Cooler",
                                short_label="CAPEX Pel_C",
                                tag="CAPEX",
                                number_of_periods=15)  # "Economics of producing fuel pellets from biomass", Mani et al., 2006


    return CAPEX_mill, CAPEX_cooler
