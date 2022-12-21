import numpy as np
import warnings

from config import settings
from configs import process_GWP_output, process_GWP_output_MC
from processes.pretreatment.utils import electricity_milling
from functions.LCA import electricity_GWP
from functions.general.utility.toml_handling import update_user_inputs_toml


def milling_GWP_MC(screensize=3.2, MC_iterations=settings.background.iterations_MC):
    """
    Calculate the GWP of feedstock milling for all Monte Carlo runs.

    Parameters
    ----------
    screensize: float
        Defines which screensize should be used for the mill.

    MC_iterations: int
        Number of Monte Carlo iterations.

    Returns
    -------

    """
    # Initialise MC output object
    MC_outputs = process_GWP_output_MC(process_name="Milling")

    # Initialise list to store particle sizes
    particle_sizes = []
    # Do analysis
    for _, count in enumerate(np.arange(MC_iterations)):
        # Initialise GWP_object
        GWP_object = process_GWP_output(process_name="Milling")

        # Calculate GWP and get resulting particle size
        electricity_requirement_milling, particle_size = electricity_milling(screensize=screensize)
        particle_sizes.append(particle_size)
        elect_GWP = electricity_GWP(electricity_requirement_milling)

        # Add to GWP object
        GWP_object.add_subprocess(name="Electricity", GWP=elect_GWP)
        GWP_object.calculate_GWP_from_subprocesses()

        # Add to MC outputs object
        MC_outputs.add_GWP_object(GWP_object)

    # Add abbreviations of subprocess'
    MC_outputs.subprocess_abbreviations = ("Elect.",)

    # Update toml document with average particle size after milling
    average_particle_size = np.mean(particle_sizes)
    if average_particle_size > settings.user_inputs["particle size"]:
        warnings.warn("Milling likely obsolete as particle size already very fine.")
    else:
        update_user_inputs_toml("particle size after milling", float(average_particle_size))

    return MC_outputs
