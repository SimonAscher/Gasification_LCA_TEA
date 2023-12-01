import numpy as np
from functions.general.utility import MJ_to_kWh
# Define models for different carbon capture process' based on analysis completed in
# analysis\preliminary\carbon_capture_energy_consumption.ipynb


def carbon_capture_VPSA_pre_comb(units="kWh"):
    """
    Calculates the energy requirements and carbon recovery rate **on a syngas basis** for a pre combustion
    vacuum pressure swing adsorption carbon capture process.
    Original data from: "http://dx.doi.org/10.1016/j.ijggc.2015.01.008"

    Parameters
    ----------
    units: str
        Either "MJ" or "kWh" to energy requirements as [MJ/kg CO2] or [kWh/kg CO2].

    Returns
    -------
    dict
        Dictionary of randomised values for "Recovery" on a syngas basis, "Electricity consumption", and
        "Heat consumption".
    """

    # Define required data
    recovery_mean = 0.873  # as decimal on a syngas basis
    recovery_std = recovery_mean * 0.1  # use an estimated std of 10%

    electricity_consumption_mean = 0.986  # [MJ/kg CO2]
    electricity_consumption_std = electricity_consumption_mean * 0.1  # [MJ/kg CO2] use an estimated std of 10%

    heat_consumption_mean = 0.51  # [MJ/ kg CO2]
    heat_consumption_std = heat_consumption_mean * 0.1  # [MJ/kg CO2] use an estimated std of 10%

    # Calculate outputs
    recovery_out = np.random.normal(recovery_mean, recovery_std)  # decimal
    electricity_out = np.random.normal(electricity_consumption_mean, electricity_consumption_std)  # [MJ/kg CO2]
    heat_out = np.random.normal(heat_consumption_mean, heat_consumption_std)  # [MJ/kg CO2]

    # Convert units to kWh
    if units == "kWh":
        electricity_out = MJ_to_kWh(electricity_out)  # [kWh/kg CO2]
        heat_out = MJ_to_kWh(heat_out)  # [kWh/kg CO2]

    return {"Recovery": recovery_out, "Electricity consumption": electricity_out, "Heat consumption": heat_out}


def carbon_capture_amine_post_comb(units="kWh"):
    """
    Calculates the energy requirements and carbon recovery rate **on a flue gas basis** for a post combustion
    amine-based carbon capture process.
    Original data from: "http://dx.doi.org/10.1016/j.ijggc.2013.03.002" and
    "http://dx.doi.org/10.1016/j.ijggc.2015.01.008"

    Parameters
    ----------
    units: str
        Either "MJ" or "kWh" to energy requirements as [MJ/kg CO2] or [kWh/kg CO2].

    Returns
    -------
    dict
        Dictionary of randomised values for "Recovery" on a flue gas basis, "Electricity consumption", and
        "Heat consumption".
    """

    # Define required data
    recovery_mean = 0.90  # as decimal on a flue gas basis
    recovery_std = recovery_mean * 0.1  # use an estimated std of 10%

    total_consumption_mean = 3.403  # [MJ/kg CO2]
    total_consumption_std = 0.342  # [MJ/kg CO2]
    total_consumption = np.random.normal(total_consumption_mean, total_consumption_std)

    electricity_fraction = np.random.normal(0.138, 0.064)
    heat_fraction = 1-electricity_fraction

    # Calculate outputs
    recovery_out = np.random.normal(recovery_mean, recovery_std)  # decimal
    electricity_out = total_consumption * electricity_fraction  # [MJ/kg CO2]
    if electricity_out < 0:
        electricity_out = 0  # Do not allow values smaller than 0
    heat_out = total_consumption * heat_fraction  # [MJ/kg CO2]
    if heat_out < 0:
        heat_out = 0  # Do not allow values smaller than 0

    # Convert units to kWh
    if units == "kWh":
        electricity_out = MJ_to_kWh(electricity_out)  # [kWh/kg CO2]
        heat_out = MJ_to_kWh(heat_out)  # [kWh/kg CO2]

    return {"Recovery": recovery_out, "Electricity consumption": electricity_out, "Heat consumption": heat_out}


def carbon_capture_VPSA_post_comb(units="kWh"):
    """
    Calculates the energy requirements and carbon recovery rate **on a flue gas basis** for a post combustion
    vacuum pressure swing adsorption carbon capture process.
    Original data from: "http://dx.doi.org/10.1016/j.jece.2017.07.029"

    Parameters
    ----------
    units: str
        Either "MJ" or "kWh" to energy requirements as [MJ/kg CO2] or [kWh/kg CO2].

    Returns
    -------
    dict
        Dictionary of randomised values for "Recovery" on a flue gas basis, "Electricity consumption", and
        "Heat consumption".
    """
    # Define required data
    recovery_mean = 0.874  # as decimal on a flue gas basis
    recovery_std = 0.073

    electricity_consumption_mean = 0.644  # [MJ/kg CO2]
    electricity_consumption_std = 0.124  # [MJ/kg CO2]

    heat_consumption = 0  # no heat required

    # Calculate outputs
    recovery_out = np.random.normal(recovery_mean, recovery_std)  # decimal
    electricity_out = np.random.normal(electricity_consumption_mean, electricity_consumption_std)  # [MJ/kg CO2]
    if electricity_out < 0:
        electricity_out = 0  # don't allow negative values
    heat_out = heat_consumption  # [MJ/kg CO2]

    # Convert units to kWh
    if units == "kWh":
        electricity_out = MJ_to_kWh(electricity_out)  # [kWh/kg CO2]
        heat_out = MJ_to_kWh(heat_out)  # [kWh/kg CO2]

    return {"Recovery": recovery_out, "Electricity consumption": electricity_out, "Heat consumption": heat_out}
