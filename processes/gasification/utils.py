import pickle

import numpy as np

from config import settings
from functions.general.utility import kJ_to_kWh
from functions.general.utility import ultimate_comp_daf_to_wb


def oxygen_for_stoichiometric_combustion(C=settings.user_inputs["carbon content"],
                                         H=settings.user_inputs["hydrogen content"],
                                         N=settings.user_inputs["nitrogen content"],
                                         S=settings.user_inputs["sulphur content"],
                                         O=settings.user_inputs["oxygen content"],
                                         moisture=settings.user_inputs["desired moisture"],
                                         ash=settings.user_inputs["ash content"]):
    """
    Get the oxygen required for the complete combustion of a given feedstock.

    Returns
    -------
    float
        Required oxygen for stoichiometric combustion [kg oxygen / kg of feedstock wb]
    """
    # Get ultimate composition as wet basis
    ultimate_comp_wb = ultimate_comp_daf_to_wb(C, H, N, S, O, moisture, ash)

    # Calculate oxygen required in kg oxygen per kg wb feedstock
    oxygen_required = 2.66 * (ultimate_comp_wb["C"] / 100) + 8 * (
            (ultimate_comp_wb["H"] / 100) - ((ultimate_comp_wb["O"] / 100) / 8)) + (ultimate_comp_wb["S"] / 100)

    return oxygen_required


def mass_agent(agent_type=settings.user_inputs["gasifying agent"], ER=settings.user_inputs["ER"], **kwargs):
    """
    Calculates the agent mass required for gasification.

    Parameters
    ----------
    agent_type: str
        Type of gasifying agent used.
    ER: float
        Equivalence ratio.
    kwargs:
        S_B_ratio (float): Steam to biomass ratio. Required when agent_type = "Steam" or "Air + steam" (default = 1).
        air_fraction (float): Fraction of air. Required when agent_type = "Air + steam".
        steam_fraction (float): Fraction of steam. Required when agent_type = "Air + steam".

    Returns
    -------
    dict
        Agent mass [kg agent / kg of feedstock wb]
    """

    # Get oxygen requirement for stoichiometric combustion in kg oxygen per kg wb feedstock
    max_oxygen = oxygen_for_stoichiometric_combustion()

    # Initialise agent mass

    if agent_type == "Air":
        agent_mass = max_oxygen * (100 / 23)  # air is 23% oxygen by weight

    elif agent_type == "Oxygen":
        agent_mass = max_oxygen  # no conversion required

    elif agent_type == "Steam":
        # Get required optional arguments
        if 'S_B_ratio' in kwargs:
            S_B_ratio = kwargs.get('S_B_ratio', None)
        else:
            S_B_ratio = 1  # Default case: Set steam to biomass ratio to 1 - based on literature research

        agent_mass = max_oxygen * (settings.data.molar_masses["H2O"] / settings.data.molar_masses["O"])
        agent_mass = agent_mass * S_B_ratio

    elif agent_type == "Air + steam":
        # Get required optional arguments
        if 'S_B_ratio' in kwargs:
            S_B_ratio = kwargs.get('S_B_ratio', None)
        else:
            S_B_ratio = 1  # Default case: Set steam to biomass ratio to 1 - based on literature research
        air_fraction = kwargs.get('air_fraction', None)
        steam_fraction = kwargs.get('steam_fraction', None)

        # Calculate mass air
        mass_air = max_oxygen * air_fraction * (100 / 23)  # air is 23% oxygen by weight
        mass_air = mass_air * ER

        # Calculate mass steam
        mass_steam = max_oxygen * steam_fraction * (settings.data.molar_masses["H2O"] / settings.data.molar_masses["O"])
        mass_steam = mass_steam * S_B_ratio * ER

    elif agent_type == "Other":
        agent_mass = max_oxygen * (100 / 23)
        raise Warning("Other gasifying agent currently not supported at this stage - treated as air.")

    else:
        raise ValueError("Wrong agent type given")

    # Scale required agent mass down by ER
    if agent_type != "Air + steam":
        mass_agent_output = {agent_type: agent_mass * ER, "units": "kg agent/kg feedstock wb"}
    else:
        mass_agent_output = {"Air": mass_air, "Steam": mass_steam, "units": "kg agent/kg feedstock wb"}

    return mass_agent_output


def load_air_separation_unit_data(full_file_path=r"C:\Users\2270577A\PycharmProjects\PhD_LCA_TEA\data"
                                                 r"\air_separation_unit_results"):
    """
    Load pickled data done in analysis on air separation unit electricity demands.
    Analysis done in: analysis/preliminary/air_separation_unit/air_separation_unit_comparison.ipynb.

    Parameters
    ----------
    full_file_path: str
    "r" string specifying the file path to pickle object.

    Returns
    -------
    dict
        Loaded air separation unit data
    """

    # Load pickled data
    loaded_data = pickle.load(open(full_file_path, "rb"))
    # TODO: Change call to file path to dynamic call - could try something like sys.path[-1]

    return loaded_data


def air_separation_unit_rng_elect_req(country=settings.user_inputs.country):
    """
    Generates a randomised electricity requirement of an air separation unit (ASU) based on normal distribution
    defined by literature values.

    Parameters
    ----------
    country

    Returns
    -------
    float
        Randomised electricity requirement of ASU [kWh el./kg O2].
    """

    # Get data - More info in analysis - air_separation_unit_comparison.ipynb
    data = load_air_separation_unit_data()
    mean = data["Mean"]
    std = data["Std"]

    # Generate random value
    value = np.random.normal(mean, std)

    return value


def steam_heat_req(mass_steam, FU=settings.general.FU):
    """
    Calculates heat requirement for steam production after applying some uncertainty.

    Parameters
    ----------
    mass_steam: float
        Required mass of steam.

    Returns
    -------
    float
        Randomised heat requirement for steam production [kWh th./ FU].
    """

    # Get some reference parameters
    room_temperature = settings.data.feedstock_drying.room_temperature  # in deg C
    boiling_temperature = 100  # in deg C

    # Calculate heat requirements
    heat_raise = (boiling_temperature - room_temperature) * settings.data.specific_heats["water"]  # [kJ/kg]
    heat_vaporisation = settings.data.heats_vaporisation.water["100 degC"]  # [kJ/kg]
    unit_heat_required = heat_raise + heat_vaporisation  # in kJ/kg steam
    total_heat_required_kJ = unit_heat_required * mass_steam * FU  # [kJ/FU]
    total_heat_required = kJ_to_kWh(total_heat_required_kJ)  # [kWh/FU]

    # Apply some uncertainty
    std_heat_required = total_heat_required * 0.1  # take std as +/- 10%
    randomised_heat_req = np.random.normal(total_heat_required, std_heat_required)

    return randomised_heat_req
