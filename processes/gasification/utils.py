from config import settings
from functions.general.utility import ultimate_comp_daf_to_wb


def oxygen_for_stoichiometric_combustion(C=settings.user_inputs["carbon content"],
                                         H=settings.user_inputs["hydrogen content"],
                                         N=settings.user_inputs["nitrogen content"],
                                         S=settings.user_inputs["sulphur content"],
                                         O=settings.user_inputs["oxygen content"],
                                         moisture=settings.user_inputs["desired moisture"],
                                         ash=settings.user_inputs["ash content"]):
    """
    Calculates the oxygen required for the complete combustion of a given feedstock.

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


def mass_agent(agent_type=None, ER=None, **kwargs):
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
    # Get defaults
    if agent_type is None:
        agent_type = settings.user_inputs["gasifying agent"]
    if ER is None:
        ER = settings.user_inputs["ER"]

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
