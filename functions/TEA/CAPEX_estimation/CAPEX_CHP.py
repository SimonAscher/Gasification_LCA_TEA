import os
import warnings

import pandas as pd
import numpy as np

from scipy.optimize import curve_fit
# from sklearn.metrics import r2_score, mean_squared_error
from config import settings
from functions.MonteCarloSimulation import get_distribution_draws
from functions.general import MAPE
from functions.general.curve_fitting import func_power_curve, func_straight_line
from functions.general.utility import get_project_root
from functions.TEA import convert_currency_annual_average
from functions.TEA.scaling import CEPCI_scale
from objects import triangular_dist_maker, PresentValue


def get_CHP_CAPEX_distribution(system_size_MWel=None, currency=None, CEPCI_year=None):
    """
    Calculate the CAPEX distribution of a CHP plant.
    CAPEX is given as total overnight cost (TOC) or total installed cost (TIC) (i.e. engineering works, procurement,
    installation, etc. are considered included in CAPEX).

    Parameters
    ----------
    system_size_MWel: None | float
        CHP size/power rating [MWel].
    currency: str | None
        Currency that is to be used for analysis.
    CEPCI_year: int | None
        Reference CEPCI year that is to be used for analysis.

    Returns
    -------
    PresentValue
        Present value object containing distribution of CAPEX values in the supplied currency.
    """

    # Get defaults

    if system_size_MWel is None:
        system_size_MWel = settings.user_inputs.system_size.power_electric_MW_el

    if currency is None:
        currency = settings.user_inputs.general.currency

    if CEPCI_year is None:
        CEPCI_year = settings.user_inputs.economic.CEPCI_year

    # Load data
    root_dir = get_project_root()
    data_file = "CAPEX_CHP.csv"
    data_file_path = os.path.join(root_dir, "data", data_file)
    df = pd.read_csv(data_file_path)

    # Convert all values to same currency and update to most recent CEPCI value
    CAPEX_currency_scaled = []
    CAPEX_currency_CEPCI_scaled = []

    for row_no in df.index:
        CAPEX_currency_scaled.append(convert_currency_annual_average(value=df["CAPEX"][row_no],
                                                                     year=df["Reference Year"][row_no],
                                                                     base_currency=df["Currency"][row_no],
                                                                     converted_currency=currency))
        CAPEX_currency_CEPCI_scaled.append(CEPCI_scale(base_year=df["Reference Year"][row_no],
                                                       design_year=CEPCI_year,
                                                       value=CAPEX_currency_scaled[row_no]))

    # Add (i) currency and (ii) currency + CEPCI scaled values to dataframe
    currency_scaled_label = "CAPEX_" + currency
    currency_and_CEPCI_scaled_label = "CAPEX_" + currency + "_CEPCI_" + str(CEPCI_year)
    df[currency_scaled_label] = CAPEX_currency_scaled
    df[currency_and_CEPCI_scaled_label] = CAPEX_currency_CEPCI_scaled

    # Add system size in MWel to df
    df["Plant size [MWel]"] = df["Plant size [kWel]"] / 1000

    # Introduce limits to data frame - i.e. discard very large data/region where data gets too sparse
    df = df[df["Plant size [MWel]"] < 500]

    # Define thresholds to split data set into small scale and medium scale plants and max allowable system size.
    threshold_small_scale_system = 5  # MW
    max_system_size = 500  # MW

    # Fit models, get performance metric, and make prediction
    if system_size_MWel <= threshold_small_scale_system:  # small scale
        df_small = df[df["Plant size [MWel]"] <= threshold_small_scale_system]

        # Fit power function based on previous analysis
        popt, _ = curve_fit(func_power_curve,
                            df_small["Plant size [MWel]"],
                            df_small[currency_and_CEPCI_scaled_label],
                            maxfev=10000)

        # Performance metrics
        # r2 = r2_score(df_small[currency_and_CEPCI_scaled_label],
        #               func_power_curve(df_small["Plant size [MWel]"], *popt))
        # rmse = mean_squared_error(df_small[currency_and_CEPCI_scaled_label],
        #                           func_power_curve(df_small["Plant size [MWel]"], *popt),
        #                           squared=False)
        mape_decimal = MAPE(df_small[currency_and_CEPCI_scaled_label],
                            func_power_curve(df_small["Plant size [MWel]"], *popt),
                            return_as_decimal=True)

        prediction = func_power_curve(system_size_MWel, *popt)

    else:  # medium scale
        if system_size_MWel < max_system_size:
            df_medium = df[(df["Plant size [MWel]"] > threshold_small_scale_system) &
                           (df["Plant size [MWel]"] <= max_system_size)]

            # Fit linear function based on previous analysis
            popt, _ = curve_fit(func_straight_line,
                                df_medium["Plant size [MWel]"],
                                df_medium[currency_and_CEPCI_scaled_label],
                                maxfev=10000)

            # Performance metrics
            # r2 = r2_score(df_medium[currency_and_CEPCI_scaled_label],
            #               func_straight_line(df_medium["Plant size [MWel]"], *popt))
            # rmse = mean_squared_error(df_medium[currency_and_CEPCI_scaled_label],
            #                           func_straight_line(df_medium["Plant size [MWel]"], *popt),
            #                           squared=False)
            mape_decimal = MAPE(df_medium[currency_and_CEPCI_scaled_label],
                                func_straight_line(df_medium["Plant size [MWel]"], *popt),
                                return_as_decimal=True)

            prediction = func_straight_line(system_size_MWel, *popt)

        else:  # too large - not supported
            raise ValueError("CHP size exceeds the supported size.")

    # Raise warnings if necessary
    if system_size_MWel < 0.05:
        warnings.warn("CHP size very small - this might lead to unexpected behaviour")

    if 5 < system_size_MWel < 10:
        warnings.warn("Region of great uncertainty "
                      "- 5MWel is the current cut off from small-scale to medium-scale system model.")

    # Get lower and upper bounds of distribution based on the distributions MAPE
    lower_bound = prediction - (prediction * mape_decimal)
    upper_bound = prediction + (prediction * mape_decimal)

    distribution = triangular_dist_maker(lower=lower_bound, mode=prediction, upper=upper_bound)

    distribution_draws = list(np.multiply(get_distribution_draws(distribution), -1))  # turn -ve as they are a cost

    CAPEX = PresentValue(values=distribution_draws,
                         name="CAPEX CHP",
                         short_label="CAPEX CHP")

    return CAPEX
