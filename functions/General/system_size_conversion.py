import pandas as pd
import numpy as np

from warnings import warn
from functions.general.utility import get_project_root
from sklearn.linear_model import LinearRegression


def convert_system_size(value, input_units, output_units, additional_outputs=False):
    """

    Parameters
    ----------
    value: float
        The value which is to be converted.
    input_units: str
         Defines the units of the "value" variable which is to be converted to the given "output_units".
         Options:
            - "tonnes/hour" - if given as feedstock mass input per hour
            - "kWh/hour" - if given as feedstock energy input per hour
            - "MWel" - if given as system size in terms of power generation

    output_units: str
        Defines the units to which the given "value" variable is to be converted.
        Options:
            - "tonnes/hour" - if given as feedstock mass input per hour
            - "kWh/hour" - if given as feedstock energy input per hour
            - "MWel" - if given as system size in terms of power generation
    additional_outputs: bool
        Defines whether additional outputs (i.e. output unit and R2 score of regressor are also to be given).
         Default = False

    Returns
    -------
    float
        System size in the selected units given by the "output_units" variable.

    """
    # Get project root and define data source
    project_root = get_project_root()
    file_name = str(project_root) + r"\data\system_size_data.csv"

    # Load data
    data = pd.read_csv(file_name, index_col=0)
    feedstock_mass_data = np.array(data["Feedstock mass input (tonnes/h)"].values)
    feedstock_energy_data = np.array(data["Feedstock energy input (kWh/h)"].values)
    power_data = np.array(data["Size electricity generation (MWe)"].values)

    # Train required model
    if input_units == "tonnes/hour" and output_units == "MWel":
        regressor = LinearRegression().fit(X=feedstock_mass_data.reshape(-1, 1), y=power_data)
        R2_score = regressor.score(X=feedstock_mass_data.reshape(-1, 1), y=power_data)
    if input_units == "kWh/hour" and output_units == "MWel":
        regressor = LinearRegression().fit(X=feedstock_energy_data.reshape(-1, 1), y=power_data)
        R2_score = regressor.score(X=feedstock_energy_data.reshape(-1, 1), y=power_data)
    if input_units == "MWel" and output_units == "tonnes/hour":
        regressor = LinearRegression().fit(X=power_data.reshape(-1, 1), y=feedstock_mass_data)
        R2_score = regressor.score(X=power_data.reshape(-1, 1), y=feedstock_mass_data)
    if input_units == "MWel" and output_units == "kWh/hour":
        regressor = LinearRegression().fit(X=power_data.reshape(-1, 1), y=feedstock_energy_data)
        R2_score = regressor.score(X=power_data.reshape(-1, 1), y=feedstock_energy_data)

    # Make prediction
    try:  # for array data
        prediction = regressor.predict(value)
    except ValueError:  # for single prediction
        prediction = float(regressor.predict(np.array(value).reshape(-1, 1)))

    # Raise warnings if data far outside of size used for training
    boundary_threshold_multiplier = 1.5
    if input_units == "tonnes/hour" and value > (boundary_threshold_multiplier * feedstock_mass_data.max()):
        warn("Input significantly outside range of training data.")
    if input_units == "kWh/hour" and value > (boundary_threshold_multiplier * feedstock_energy_data.max()):
        warn("Input significantly outside range of training data.")
    if input_units == "MWel" and value > (boundary_threshold_multiplier * power_data.max()):
        warn("Input significantly outside range of training data.")

    if value < 0:
        raise ValueError("Input value must be positive.")

    # Determine function output
    if additional_outputs:
        output = {"value": prediction, "units": output_units, "R2_score": R2_score}
    else:
        output = prediction

    return output


# # Examples
# ex_1 = convert_system_size(4000, "kWh/hour", "MWel")
# ex_2 = convert_system_size(1, "MWel", "kWh/hour")
# ex_3 = convert_system_size(1.8, "tonnes/hour", "MWel")
# ex_4 = convert_system_size(1, "MWel", "tonnes/hour")
# ex_3 = convert_system_size(10, "tonnes/hour", "MWel")  # Note: Raises error correctly.
