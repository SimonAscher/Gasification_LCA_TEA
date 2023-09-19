import pandas as pd
import numpy as np

from config import settings
from functions.general.utility import get_project_root, MJ_to_kWh
from sklearn.linear_model import LinearRegression
from typing import Literal

_input_output_unit_types = Literal["tonnes/hour", "MWh/hour", "MWel"]


def convert_system_size(value, input_units: _input_output_unit_types, feedstock_LHV=None):
    """
    Convert between a range of different system size units.

    Parameters
    ----------
    value: float
        The value which is to be converted.
    input_units: _input_output_unit_types
         Defines the units of the "value" variable which is to be converted to the given "output_units".
         Options:
            - "tonnes/hour" - if given as feedstock mass input per hour
            - "MWh/hour" - if given as feedstock energy input per hour
            - "MWel" - if given as system size in terms of electric power generation
    feedstock_LHV: None | float | int
        Feedstock lower heating value [MJ/kg].

    Returns
    -------
    dict
        Dictionary of system sizes in the three units.
    """

    # Get default values
    if feedstock_LHV is None:
        feedstock_LHV = settings.user_inputs.feedstock.LHV  # [MJ/kg]

    # Get project root and define data source
    project_root = get_project_root()
    file_name = str(project_root) + r"\data\system_size_data.csv"

    # Load data
    data = pd.read_csv(file_name, index_col=0)
    feedstock_mass_data = np.array(data["Feedstock mass input (tonnes/h)"].values)
    power_data = np.array(data["Size electricity generation (MWe)"].values)

    if input_units == "tonnes/hour":
        size_feedstock_mass = value  # [tonnes/hour]
        size_feedstock_energy = MJ_to_kWh(size_feedstock_mass * feedstock_LHV * 1000) / 1000  # [MWh/hour]

        # Get size power from regression
        if size_feedstock_mass < 2:
            regressor = LinearRegression().fit(X=feedstock_mass_data[feedstock_mass_data < 2].reshape(-1, 1),
                                               y=power_data[feedstock_mass_data < 2])
            R2_score = regressor.score(X=feedstock_mass_data[feedstock_mass_data < 2].reshape(-1, 1),
                                       y=power_data[feedstock_mass_data < 2])
        else:
            regressor = LinearRegression().fit(X=feedstock_mass_data.reshape(-1, 1), y=power_data)
            R2_score = regressor.score(X=feedstock_mass_data.reshape(-1, 1), y=power_data)

        # Get prediction
        size_power = float(regressor.predict(np.array(size_feedstock_mass).reshape(-1, 1)))  # [MWel]

    if input_units == "MWh/hour":
        size_feedstock_energy = value  # [MWh/hour]
        size_feedstock_mass = MJ_to_kWh(value=size_feedstock_energy * 1000, reverse=True) / (
                    feedstock_LHV * 1000)  # [tonnes/hour]

        # Get size power from regression
        if size_feedstock_mass < 2:
            regressor = LinearRegression().fit(X=feedstock_mass_data[feedstock_mass_data < 2].reshape(-1, 1),
                                               y=power_data[feedstock_mass_data < 2])
            R2_score = regressor.score(X=feedstock_mass_data[feedstock_mass_data < 2].reshape(-1, 1),
                                       y=power_data[feedstock_mass_data < 2])
        else:
            regressor = LinearRegression().fit(X=feedstock_mass_data.reshape(-1, 1), y=power_data)
            R2_score = regressor.score(X=feedstock_mass_data.reshape(-1, 1), y=power_data)

        # Get prediction
        size_power = float(regressor.predict(np.array(size_feedstock_mass).reshape(-1, 1)))  # [MWel]

    if input_units == "MWel":
        size_power = value  # [MWel]

        # Get size in mass basis from regression
        if size_power < 2:
            regressor = LinearRegression().fit(X=power_data[power_data < 2].reshape(-1, 1),
                                               y=feedstock_mass_data[power_data < 2])
            R2_score = regressor.score(X=power_data[power_data < 2].reshape(-1, 1),
                                       y=feedstock_mass_data[power_data < 2])
        else:
            regressor = LinearRegression().fit(X=power_data.reshape(-1, 1), y=feedstock_mass_data)
            R2_score = regressor.score(X=power_data.reshape(-1, 1), y=feedstock_mass_data)

        # Get prediction
        size_feedstock_mass = float(regressor.predict(np.array(size_power).reshape(-1, 1)))  # [tonnes/hour]

        size_feedstock_energy = MJ_to_kWh(size_feedstock_mass * feedstock_LHV * 1000) / 1000  # [MWh/hour]

        # Run some checks
        if input_units not in ["MWel", "MWh/hour", "tonnes/hour"]:
            raise ValueError("Supplied units are not supported.")

        if value < 0:
            raise ValueError("Input value must be positive.")

    output_dict = {"size_feedstock_mass": size_feedstock_mass,
                   "size_feedstock_energy": size_feedstock_energy,
                   "size_power": size_power}

    return output_dict

    # TODO: Change all function calls so they work with this - note now return in MWh not kWh!!!

    # TODO: Make sure streamlit supplies LHV directly to function.
