import warnings
from config import settings
from configs import process_GWP_output, process_GWP_output_MC
from functions.general.utility import kJ_to_kWh
from functions.LCA import electricity_GWP, thermal_energy_GWP
from processes.pretreatment.utils import energy_drying


def drying_GWP(energy_drying_dict=None):
    """
    Calculates the GWP due to energy demand for drying.

    Parameters
    ----------
    energy_drying_dict: dict
        Output from energy_drying function containing heat and electricity requirements and units and heat source.

    Returns
    -------
        GWP values in kg CO2eq./FU.
    """
    # Get defaults
    if energy_drying_dict is None:
        energy_drying_dict = energy_drying()

    # Initialise output object
    output_GWP = process_GWP_output(process_name="Feedstock drying")

    # Convert units to kWh if not given in kWh already
    if energy_drying_dict["units"] == "kJ":
        energy_drying_dict["heat"] = kJ_to_kWh(energy_drying_dict["heat"])
        energy_drying_dict["electricity"] = kJ_to_kWh(energy_drying_dict["electricity"])
        energy_drying_dict["units"] = "kWh"

    # Calculate impact due to electricity usage
    electric_GWP = electricity_GWP(energy_drying_dict["electricity"])

    # Calculate impact due to heat demands
    if energy_drying_dict["heat source"] == "natural gas":
        heat_GWP = thermal_energy_GWP(amount=energy_drying_dict["heat"],
                                      source=energy_drying_dict["heat source"],
                                      units=energy_drying_dict["units"]
                                      )

    # Add values to output object
    output_GWP.add_subprocess(name="Electricity", GWP=electric_GWP)
    output_GWP.add_subprocess(name="Thermal energy", GWP=heat_GWP)
    output_GWP.GWP = electric_GWP + heat_GWP

    # TODO: Implement solar drying and waste heat drying - would mean no energy req for drying
    #  or much lower requirement, respectively

    # TODO: Implement syngas use - make sure model accounts for less syngas being available for CHP etc. - would use
    #  energy for drying - see how much syngas that corresponds to and then calculate emissions from combusting this
    #  much syngas using existing function
    return output_GWP


def drying_GWP_MC(MC_iterations=settings.background.iterations_MC):
    """
    Calculate the GWP of feedstock drying for all Monte Carlo runs.

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
    MC_outputs = process_GWP_output_MC(process_name="Feedstock Drying")

    for _ in list(range(MC_iterations)):
        # Calculate individual GWPs
        GWP_object = drying_GWP()

        # Store in output object
        MC_outputs.add_GWP_object(GWP_object)

    MC_outputs.subprocess_abbreviations = ("Elect.", "Heat", )  # add abbreviation of subprocess

    return MC_outputs
