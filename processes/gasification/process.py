from config import settings
import numpy as np
from configs import process_requirements, process_GWP_output, process_GWP_output_MC
from functions.LCA import thermal_energy_GWP, electricity_GWP
from functions.general.utility import kJ_to_kWh
from processes.gasification.utils import mass_agent
from processes.general import oxygen_rng_elect_req, steam_rng_heat_req

# file to calculate gasification outputs
# i.e. how much biochar and how much syngas is produced
# prediction model can be used for that

"""
Energy requirements for:
    - operation of gasifier (fixed, fluidised, aux demands, scale, etc)
    - provision of agent (air, steam, O2)
"""
def gasification_requirements(operation_mode=settings.user_inputs["operation mode"],
                              operation_scale=settings.user_inputs["operation scale"],
                              agent_type=settings.user_inputs["gasifying agent"],
                              agent_mass=None,
                              catalyst=settings.user_inputs["catalyst"],
                              reactor_type=settings.user_inputs["reactor type"],
                              bed_material=settings.user_inputs["bed material"],
                              FU=settings.general["FU"]):
    """
    Calculates all electricity, heat, and direct GWP requirements from the gasification process.

    Parameters
    ----------
    operation_mode
    operation_scale
    agent_type
    agent_mass
    catalyst
    reactor_type
    bed_material
    FU

    Returns
    -------
    dict
        Dictioniary of requirements using the following units:
            - Heat [kWh/FU]
            - Electricity [kWh/FU]
            - GWP [kg CO2eq./FU]
    """
    # TODO: Add aux demands and demands based on reactor type etc.

    # Define defaults
    if agent_mass is None:
        agent_mass = mass_agent()

    # Initialise dictionary to store all requirements - append to requirement lists
    requirements = process_requirements(name="gasification_requirements")

    # Model emissions and energy requirements based on agent type
    if agent_type == "Air" or agent_type == "Other":
        # Note: Currently agent_type = "Other" treated as air.
        # Note: Currently no direct emissions due to agent
        pass
    elif agent_type == "Air + steam":
        pass

    elif agent_type == "Oxygen":
        total_oxygen_mass = agent_mass["Oxygen"] * FU  # [kg/FU]
        total_oxygen_electricity_req = total_oxygen_mass * oxygen_rng_elect_req()
        requirements.add_subprocess("Agent", electricity=total_oxygen_electricity_req)

    elif agent_type == "Steam":
        # Get heat requirement for steam production
        heat_req_steam = steam_rng_heat_req(mass_steam=agent_mass["Steam"])
        requirements.add_subprocess("Agent", heat=heat_req_steam)  # add to requirements object
    else:
        raise ValueError("Wrong agent type given")

    return requirements


def gasification_GWP(requirements=None):
    """
    Calculates the GWP resulting from the heat and electricity requirements of the gasification process.

    Parameters
    ----------
    requirements: object
        Process requirements object of calculated gasification requirements.

    Returns
    -------

    """

    # Use this syntax to assign default to ensure requirements is run new every time.
    if requirements is None:
        requirements = gasification_requirements()

    # Initialise output object
    output_GWP = process_GWP_output(process_name="Gasification")

    # Add GWP of subprocesses to GWP object
    for count, subprocess_label in enumerate(requirements.subprocess_names):
        output_GWP.add_subprocess(name=subprocess_label, GWP=requirements.subprocess_total_GWP[count])

    # Get total GWP
    output_GWP.calculate_GWP_from_subprocesses()

    return output_GWP


def gasification_GWP_MC(MC_iterations=settings.background.iterations_MC):
    """
    Calculate the GWP of gasification for all Monte Carlo runs.

    Parameters
    ----------
    MC_iterations: int
        Number of Monte Carlo iterations.

    Returns
    -------
    object
        process_GWP_output_MC object storing all simulation results.
    """
    # Initialise output object
    MC_outputs = process_GWP_output_MC(process_name="Gasification")

    for _ in list(range(MC_iterations)):
        # Calculate individual GWPs
        GWP_object = gasification_GWP()
        # Note: Currently all default values used - add distributions if non-fixed values are to be used. For this
        # could add "iterations" variable in for loop which could then be used to draw sample from the distibutions
        # and put into "gasification_GWP" function. For this would likely want to add kwargs which then could be used
        # as inputs to e.g. "gasification_GWP" or even "gasification_requirements" functions.

        # Store in output object
        MC_outputs.add_GWP_object(GWP_object)

    MC_outputs.subprocess_abbreviations = ("Agent",)  # add abbreviation of subprocess

    return MC_outputs
