import pickle

import numpy as np

from config import settings
from functions.general.utility import ultimate_comp_daf_to_wb, get_project_root
from functions.general.utility import MJ_to_kWh
from processes.CHP import CombinedHeatPower
from functions.MonteCarloSimulation import get_distribution_draws


def oxygen_for_stoichiometric_combustion(C=settings.user_inputs.feedstock.carbon,
                                         H=settings.user_inputs.feedstock.hydrogen,
                                         N=settings.user_inputs.feedstock.nitrogen,
                                         S=settings.user_inputs.feedstock.sulphur,
                                         O=settings.user_inputs.feedstock.oxygen,
                                         moisture=None,
                                         ash=settings.user_inputs.feedstock.ash):
    """
    Calculates the oxygen required for the complete combustion of a given feedstock.
    By default, takes feedstock data given by user.

    Returns
    -------
    float
        Required oxygen for stoichiometric combustion [kg oxygen / kg of feedstock wb]
    """
    # Get defaults
    if moisture is None:
        try:
            moisture = settings.user_inputs.feedstock.moisture_post_drying
        except:
            moisture = settings.user_inputs.feedstock.moisture_ar

    # Get ultimate composition as wet basis
    ultimate_comp_wb = ultimate_comp_daf_to_wb(C, H, N, S, O, moisture, ash)

    # Calculate oxygen required in kg oxygen per kg wb feedstock
    oxygen_required = 2.66 * (ultimate_comp_wb["C"] / 100) + 8 * (
            (ultimate_comp_wb["H"] / 100) - ((ultimate_comp_wb["O"] / 100) / 8)) + (ultimate_comp_wb["S"] / 100)

    return oxygen_required


def mass_agent(agent_type=None, ER=None, **kwargs):
    """
    Calculates the agent mass required for gasification.
    By default, takes agent type and ER data given by user.

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
    # Get defaults
    if agent_type is None:
        agent_type = settings.user_inputs.process_conditions.gasifying_agent
    if ER is None:
        ER = settings.user_inputs.process_conditions.ER

    # Get oxygen requirement for stoichiometric combustion in kg oxygen per kg wb feedstock
    max_oxygen = oxygen_for_stoichiometric_combustion()

    # Initialise agent mass
    agent_mass = None
    mass_air = None
    mass_steam = None

    if agent_type == "Air":
        agent_mass = max_oxygen * (1 / 0.23)  # air is 23% oxygen by weight

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
        mass_air = max_oxygen * air_fraction * (1 / 0.23)  # air is 23% oxygen by weight
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


def load_gasification_aux_electricity_demands_data(full_file_path=None):
    """
    Load pickled data done in analysis on gasification and gas cleaning auxiliary electricity demands.
    Analysis done in: analysis/preliminary/gas_cleaning_and_aux_demands/gas_cleaning_and_aux_demands.ipynb.

    Parameters
    ----------
    full_file_path: str
    "r" string specifying the file path to pickle object.

    Returns
    -------
    dict
        Loaded data on requirements for gas cleaning and auxiliary gasification demands.
    """
    if full_file_path is None:
        project_root = get_project_root()
        full_file_path = str(project_root) + r"\data\gasification_aux_demands_results"

    # Load pickled data
    loaded_data = pickle.load(open(full_file_path, "rb"))

    return loaded_data


def load_gasification_aux_heat_demands_data(full_file_path=None):
    """
    Load pickled data done in analysis on gasification and gas cleaning auxiliary heat demands.
    Analysis done in: analysis/preliminary/gas_cleaning_and_aux_demands/heat_requirements.ipynb.

    Parameters
    ----------
    full_file_path: str
    "r" string specifying the file path to pickle object.

    Returns
    -------
    dict
        Loaded data on requirements for gas cleaning and auxiliary gasification demands.
    """
    if full_file_path is None:
        project_root = get_project_root()
        full_file_path = str(project_root) + r"\data\gasification_aux_heat_demands_results"

    # Load pickled data
    loaded_data = pickle.load(open(full_file_path, "rb"))

    return loaded_data


def demands_ele_aux_gas_cleaning(C=settings.user_inputs.feedstock.carbon,
                                 H=settings.user_inputs.feedstock.hydrogen,
                                 S=settings.user_inputs.feedstock.sulphur,
                                 moisture=None):
    """
    Calculates electricity requirements for auxiliary gasification operations and syngas cleaning.

    Parameters
    ----------
    C: float
        Carbon content of feedstock [% daf].
    H: float
        Hydrogen content of feedstock [% daf].
    S: float
        Sulphur content of feedstock [% daf].
    moisture: float
        Moisture content of feedstock [% wb].

    Returns
    -------
    float
        Electricity requirement for auxiliary gasification demands and gas cleaning.
    """
    # Get defaults
    if moisture is None:
        try:
            moisture = settings.user_inputs.feedstock.moisture_post_drying
        except:
            moisture = settings.user_inputs.feedstock.moisture_ar

    # Get feedstock LHV
    feedstock_LHV = settings.user_inputs.feedstock.LHV  # MJ/kg wb

    feedstock_mass = settings.general.FU
    total_feedstock_energy = MJ_to_kWh(value=(feedstock_mass * feedstock_LHV))

    # Get data on requirements for auxiliary and gas cleaning
    aux_requirements_data = load_gasification_aux_electricity_demands_data()

    # Draw sample from triangular_dist_maker distribution.
    aux_fraction = np.random.default_rng().triangular(left=aux_requirements_data.lower,
                                                      mode=aux_requirements_data.mode,
                                                      right=aux_requirements_data.upper)
    # Calculate auxiliary energy requirements
    aux_energy = aux_fraction * total_feedstock_energy

    return aux_energy


def demands_heat_auxiliary_gasification(CHP_results_object=None,
                                        MC_iterations=None):
    # Get defaults
    if CHP_results_object is None:
        CHP_results_object = CombinedHeatPower()

    if MC_iterations is None:
        MC_iterations = settings.user_inputs.general.MC_iterations

    heat_production = CHP_results_object.requirements[0].heat[0].values

    aux_heat_reqs_data = load_gasification_aux_heat_demands_data()

    dist_draws = get_distribution_draws(distribution_maker=aux_heat_reqs_data, length_array=MC_iterations)

    aux_heat_demands = list(np.array(heat_production) * dist_draws)

    return aux_heat_demands
