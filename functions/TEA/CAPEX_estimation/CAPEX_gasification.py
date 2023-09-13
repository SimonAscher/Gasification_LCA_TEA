import math
import os
import warnings

import numpy as np
import pandas as pd

from typing import Literal
from scipy.optimize import curve_fit
from config import settings
from functions.MonteCarloSimulation import get_distribution_draws
from functions.general import MAPE, convert_system_size
from functions.general.curve_fitting import func_power_curve, func_straight_line
from functions.general.utility import get_project_root
from functions.TEA import convert_currency_annual_average
from functions.TEA.scaling import CEPCI_scale
from objects import triangular_dist_maker, PresentValue

_system_size_unit_types = Literal["tonnes/hour", "MW_feedstock_LHV", "MWel"]


def get_gasification_and_gas_cleaning_CAPEX_distributions(system_size,
                                                          system_size_units: _system_size_unit_types = "MWel",
                                                          reactor_type=None, currency=None,
                                                          CEPCI_year=None):
    """
    Calculate the CAPEX distribution of a gasification plant with syngas cleaning.
    CAPEX is given as total overnight cost (TOC) or total installed cost (TIC) (i.e. engineering works, procurement,
    installation, etc. are considered included in CAPEX).

    Parameters
    ----------
    system_size: float
        Gasification size in units supplied by "system_size_units" parameter.
    system_size_units: _system_size_unit_types
        Defines the units of the "system_size" variable.
        Options:
            - "MWel" - System size in terms of electric power generation/power rating
            - "tonnes/hour" - System size in terms of feedstock mass input per hour
            - "MW_feedstock_LHV" - System size in terms of feedstock energy input (same as MWh_feedstock_LHV/hour).
    reactor_type: str | None
        Selected reactor type ("Fluidised bed" or "Fixed bed"). If None this is taken from user input settings.
    currency: str | None
        Currency that is to be used for analysis.
    CEPCI_year: int | None
        Reference CEPCI year that is to be used for analysis.

    Returns
    -------
    tuple[PresentValue, PresentValue]
        Tuple of present value objects containing distribution of CAPEX values in the supplied currency.
        1st tuple entry = CAPEX of gasification plant. 2nd tuple entry = CAPEX of syngas cleaning.
    """

    # Get defaults
    if currency is None:
        currency = settings.user_inputs.general.currency

    if CEPCI_year is None:
        CEPCI_year = settings.user_inputs.economic.CEPCI_year

    if reactor_type is None:
        reactor_type = settings.user_inputs.process_conditions.reactor_type

    # Check that system size is supplied in valid units.
    system_size_unit_types = ["tonnes/hour", "MW_feedstock_LHV", "MWel"]

    # Model uses system size as MWel - if supplied in other units convert to that
    if system_size_units == "MWel":
        system_size_MWel = system_size

    elif system_size_units == "tonnes/hour":
        system_size_MWel = convert_system_size(value=system_size,
                                               input_units="tonnes/hour",
                                               output_units="MWel")

    elif system_size_units == "MW_feedstock_LHV":
        system_size_MWel = convert_system_size(value=system_size * 1000,
                                               input_units="kWh/hour",
                                               output_units="MWel")

    else:
        raise ValueError(f"Invalid system size unit. Expected one of: {system_size_unit_types}")

    # Load data
    root_dir = get_project_root()
    data_file = "CAPEX_Gasification.csv"
    data_file_path = os.path.join(root_dir, "data", data_file)
    df_source = pd.read_csv(data_file_path)
    df = df_source.copy()  # working copy of df

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

    # Fill in missing size data based on size data in different units
    # Fill in plant size [tonnes/hour] data
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        for count, value in enumerate(df_source["Plant size [tonnes/hour]"]):
            if math.isnan(value):
                plant_size_kWh_per_hour_feedstock = df.loc[count, "Plant size [MW feedstock LHV] or [MWh/hour]"] * 1000
                plant_size_MWel = df.loc[count, "Plant size [MWel]"]

                if not math.isnan(plant_size_kWh_per_hour_feedstock):  # replace based on plant_size_MW_feedstock first
                    converted_value = convert_system_size(value=plant_size_kWh_per_hour_feedstock,
                                                          input_units="kWh/hour",
                                                          output_units="tonnes/hour")
                else:
                    if not math.isnan(plant_size_MWel):  # otherwise replace based on plant_size_MWel
                        converted_value = convert_system_size(value=plant_size_MWel,
                                                              input_units="MWel",
                                                              output_units="tonnes/hour")
                    else:  # no suitable reference value to convert from - leave as nan
                        converted_value = np.NAN
                # populate data frame
                df.loc[count, ["Plant size [tonnes/hour]"]] = converted_value

        # Fill in plant size [MWel] data
        for count, value in enumerate(df_source["Plant size [MWel]"]):
            if math.isnan(value):
                plant_size_kWh_per_hour_feedstock = df.loc[count, "Plant size [MW feedstock LHV] or [MWh/hour]"] * 1000
                plant_size_tonnes_per_hour = df.loc[count, "Plant size [tonnes/hour]"]

                if not math.isnan(plant_size_kWh_per_hour_feedstock):  # replace based on plant_size_MW_feedstock first
                    converted_value = convert_system_size(value=plant_size_kWh_per_hour_feedstock,
                                                          input_units="kWh/hour",
                                                          output_units="MWel")
                else:
                    if not math.isnan(plant_size_tonnes_per_hour):  # otherwise replace based on plant_size_tonnes_per_hour
                        converted_value = convert_system_size(value=plant_size_tonnes_per_hour,
                                                              input_units="tonnes/hour",
                                                              output_units="MWel")
                    else:  # no suitable reference value to convert from - leave as nan
                        converted_value = np.NAN
                # populate data frame
                df.loc[count, ["Plant size [MWel]"]] = converted_value

        # Fill in plant size [MW feedstock LHV] or [MWh/hour] data
        for count, value in enumerate(df_source["Plant size [MW feedstock LHV] or [MWh/hour]"]):
            if math.isnan(value):
                plant_size_MWel = df.loc[count, "Plant size [MWel]"]
                plant_size_tonnes_per_hour = df.loc[count, "Plant size [tonnes/hour]"]

                if not math.isnan(plant_size_MWel):  # replace based on plant_size_MWel
                    converted_value = convert_system_size(value=plant_size_MWel,
                                                          input_units="MWel",
                                                          output_units="kWh/hour") / 1000
                else:
                    if not math.isnan(plant_size_tonnes_per_hour):  # otherwise replace based on plant_size_tonnes_per_hour
                        converted_value = convert_system_size(value=plant_size_tonnes_per_hour,
                                                              input_units="tonnes/hour",
                                                              output_units="kWh/hour") / 1000
                    else:  # no suitable reference value to convert from - leave as nan
                        converted_value = np.NAN
                # populate data frame
                df.loc[count, ["Plant size [MW feedstock LHV] or [MWh/hour]"]] = converted_value

    # Add new column which indicates whether gas cleaning and power generation are included in cost data
    cleaning_and_power_generation = []
    for row_no in df.index:
        gas_cleaning_cond = False
        power_gen_cond = False
        if df["Gas Cleaning Included"][row_no] and df["Power Generation Included"][row_no]:
            label = "Gas Cleaning + Power Generation"
        elif df["Gas Cleaning Included"][row_no] and not df["Power Generation Included"][row_no]:
            label = "Gas Cleaning"
        elif not df["Gas Cleaning Included"][row_no] and df["Power Generation Included"][row_no]:
            label = "Power Generation"
        else:
            label = "Gasification only"

        cleaning_and_power_generation.append(label)

    # Add cleaning and power generation descriptors to df
    df["Cleaning and Power Generation"] = cleaning_and_power_generation

    # Add additional cost column which excludes cleaning cost if cleaning was included in cost
    label_CAPEX_scaled_without_cleaning = "CAPEX_scaled_without_cleaning"
    gas_cleaning_fraction_of_total_CAPEX_mode = 0.24
    df[label_CAPEX_scaled_without_cleaning] = np.array(np.where(df["Cleaning and Power Generation"] != "Gasification only",
                                                                df[currency_and_CEPCI_scaled_label] *
                                                                (1-gas_cleaning_fraction_of_total_CAPEX_mode),
                                                                df[currency_and_CEPCI_scaled_label]))
    """
    Note: 
    Literature indicates that gas cleaning costs make up 17, 24, and 33 % of the overall gasification scheme
        - References:
            - https://doi.org/10.1002/er.3038
            - https://doi.org/10.1002/bbb.137
            - "Process Design and Economics for Conversion of Lignocellulosic Biomass to Ethanol: Thermochemical Pathway by 
               Indirect Gasification and Mixed Alcohol Synthesis"
    """

    # Manually remove one extreme outlier in the data
    df = df[df["Reference"] != "https://doi.org/10.1016/j.compchemeng.2020.106758"].copy()

    # Introduce limits to main data frame - i.e. discard very large data/region where data gets too sparse
    df = df[df["Plant size [MWel]"] < 100].copy()

    # Define thresholds to split data set into small scale and medium scale plants and max allowable system size.
    threshold_small_scale_system = 5  # MWel
    max_fluidised_bed_size = 70  # MWel
    max_fixed_bed_size = 15  # MWel

    # Get dataframes for fixed bed and fluidised bed data only
    df_fluidised = df[df["Type"] == "fluidised bed"]
    df_fixed = df[df["Type"] == "fixed bed"]

    # Fit models, get performance metric, and make prediction
    # Small-scale fluidised bed reactor
    if system_size_MWel <= threshold_small_scale_system and reactor_type == "Fluidised bed":
        df_selected = df[df["Plant size [MWel]"] < threshold_small_scale_system]

        # Fit power function based on previous analysis
        popt, _ = curve_fit(f=func_power_curve,
                            xdata=df_selected["Plant size [MWel]"],
                            ydata=df_selected[label_CAPEX_scaled_without_cleaning],
                            maxfev=10000)

        mape_decimal = MAPE(df_selected[label_CAPEX_scaled_without_cleaning],
                            func_power_curve(df_selected["Plant size [MWel]"], *popt),
                            return_as_decimal=True)

        prediction = func_power_curve(system_size_MWel, *popt)

    # Medium to large scale fluidised bed reactor
    if threshold_small_scale_system < system_size_MWel < max_fluidised_bed_size and reactor_type == "Fluidised bed":
        df_selected = df_fluidised[df_fluidised["Plant size [MWel]"] > threshold_small_scale_system]

        # Fit power function based on previous analysis
        popt, _ = curve_fit(f=func_power_curve,
                            xdata=df_selected["Plant size [MWel]"],
                            ydata=df_selected[label_CAPEX_scaled_without_cleaning],
                            maxfev=10000)

        mape_decimal = MAPE(df_selected[label_CAPEX_scaled_without_cleaning],
                            func_power_curve(df_selected["Plant size [MWel]"], *popt),
                            return_as_decimal=True)

        prediction = func_power_curve(system_size_MWel, *popt)

    # Fixed bed reactor smaller than 15MWel
    if system_size_MWel <= max_fixed_bed_size and reactor_type == "Fixed bed":
        df_selected = df_fixed

        # Fit power function based on previous analysis
        popt, _ = curve_fit(f=func_straight_line,
                            xdata=df_selected["Plant size [MWel]"],
                            ydata=df_selected[label_CAPEX_scaled_without_cleaning],
                            maxfev=10000)

        mape_decimal = MAPE(df_selected[label_CAPEX_scaled_without_cleaning],
                            func_straight_line(df_selected["Plant size [MWel]"], *popt),
                            return_as_decimal=True)

        prediction = func_straight_line(system_size_MWel, *popt)

    # Fixed bed reactor larger than 15MWel - default to same model as fluidised bed reactor and display warning
    if max_fixed_bed_size < system_size_MWel < max_fluidised_bed_size and reactor_type == "Fixed bed":
        warnings.warn("Fixed bed gasifier only supported up to a rating of 15 MWel - defaulted to fluidised bed gasifier "
                      "CAPEX model.")
        df_selected = df_fluidised[df_fluidised["Plant size [MWel]"] > threshold_small_scale_system]

        # Fit power function based on previous analysis
        popt, _ = curve_fit(f=func_power_curve,
                            xdata=df_selected["Plant size [MWel]"],
                            ydata=df_selected[label_CAPEX_scaled_without_cleaning],
                            maxfev=10000)

        mape_decimal = MAPE(df_selected[label_CAPEX_scaled_without_cleaning],
                            func_power_curve(df_selected["Plant size [MWel]"], *popt),
                            return_as_decimal=True)

        prediction = func_power_curve(system_size_MWel, *popt)

    # Raise warnings if necessary
    if system_size_MWel > max_fluidised_bed_size:
        warnings.warn("System size limited to 70 MWel. Given value exceeds this.")

    # Gasification costs
    # Get lower and upper bounds of distribution based on the distributions MAPE
    lower_bound_gasification = prediction - (prediction * mape_decimal)
    upper_bound_gasification = prediction + (prediction * mape_decimal)

    dist_draws_gasification = list(get_distribution_draws(triangular_dist_maker(lower=lower_bound_gasification,
                                                                                mode=prediction,
                                                                                upper=upper_bound_gasification)))

    # Gas cleaning costs

    # Gas cleaning cost fractions of total cost. See note at the start of script more information.
    gas_cleaning_fraction_of_total_CAPEX_lower = 0.17
    gas_cleaning_fraction_of_total_CAPEX_upper = 0.33
    # mode value = 0.24 (defined above)

    # Gas cleaning fraction distribution and draws
    dist_draws_gas_cleaning_fraction_decimal = list(get_distribution_draws(
        triangular_dist_maker(lower=gas_cleaning_fraction_of_total_CAPEX_lower,
                              mode=gas_cleaning_fraction_of_total_CAPEX_mode,
                              upper=gas_cleaning_fraction_of_total_CAPEX_upper)))

    dist_draws_gas_cleaning = []
    for count, gasification_CAPEX_draw in enumerate(dist_draws_gasification):
        dist_draws_gas_cleaning.append((gasification_CAPEX_draw / (1-gas_cleaning_fraction_of_total_CAPEX_mode)) *
                                       dist_draws_gas_cleaning_fraction_decimal[count])

    # Store CAPEX distributions in PresentValue objects.
    CAPEX_gasification = PresentValue(values=dist_draws_gasification,
                                      name="CAPEX gasification",
                                      short_label="CAPEX gas.")

    CAPEX_gas_cleaning = PresentValue(values=dist_draws_gas_cleaning,
                                      name="CAPEX gas cleaning",
                                      short_label="CAPEX gas clean.")

    return CAPEX_gasification, CAPEX_gas_cleaning
