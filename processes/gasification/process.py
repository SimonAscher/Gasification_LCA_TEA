from config import settings
from configs import process_requirements, process_GWP_output, process_GWP_output_MC
from functions.LCA import thermal_energy_GWP, electricity_GWP
from functions.general.utility import kJ_to_kWh
from processes.gasification import mass_agent

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
                              agent_mass=mass_agent(),
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
        total_oxygen_GWP = total_oxygen_mass * settings.data.CO2_equivalents.resource_requirements["oxygen"]  # [kgCO2eq./FU]
        requirements.add_subprocess("Agent", GWP=total_oxygen_GWP)  # add to requirements object
        # TODO: Currently this value seems too low - 1/10th of steam - look into it again - maybe other source than GaBi

    elif agent_type == "Steam":
        # Get some reference parameters
        room_temperature = settings.data.feedstock_drying.room_temperature  # in deg C
        boiling_temperature = 100  # in deg C

        # Calculate heat requirements
        heat_raise = (boiling_temperature - room_temperature) * settings.data.specific_heats["water"]  # [kJ/kg]
        heat_vaporisation = settings.data.heats_vaporisation.water["100 degC"]  # [kJ/kg]
        unit_heat_required = heat_raise + heat_vaporisation  # in kJ/kg steam
        total_heat_required_kJ = unit_heat_required * agent_mass["Steam"] * FU  # [kJ/FU]
        total_heat_required = kJ_to_kWh(total_heat_required_kJ)  # [kWh/FU]
        requirements.add_subprocess("Agent", heat=total_heat_required)  # add to requirements object
    else:
        raise ValueError("Wrong agent type given")

    return requirements


def gasification_GWP(requirements=gasification_requirements()):
    """
    Calculates the GWP resulting from the heat and electricity requirements of the gasification process.

    Parameters
    ----------
    requirements: object
        Process requirements object of calculated gasification requirements.

    Returns
    -------

    """
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

    return MC_outputs
