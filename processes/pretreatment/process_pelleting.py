import numpy as np

from config import settings
from configs import process_GWP_output, process_GWP_output_MC
from processes.pretreatment.utils import electricity_pelleting
from functions.LCA import electricity_GWP
from functions.general.utility.toml_handling import update_user_inputs_toml


def pelleting_GWP_MC(particle_size=None, MC_iterations=settings.background.iterations_MC):
    """
    Calculate the GWP of feedstock pelleting for all Monte Carlo runs.
    Note: Ensure that milling function is run first to update particle size post milling.

    Parameters
    ----------
    particle_size: float
        Defines the particle size in mm. Uses post milling particle size if applicable.

    MC_iterations: int
        Number of Monte Carlo iterations.

    Returns
    -------

    """
    # Get defaults
    if particle_size is None:
        try:
            particle_size = settings.user_inputs["particle size after milling"]
        except:
            particle_size = settings.user_inputs["particle size"]

    # Initialise MC output object
    MC_outputs = process_GWP_output_MC(process_name="Pelleting")

    # Do analysis
    for _, count in enumerate(np.arange(MC_iterations)):
        # Initialise GWP_object
        GWP_object = process_GWP_output(process_name="Pelleting")

        # Calculate GWP
        electricity_requirement_pelleting = electricity_pelleting(particle_size=particle_size)
        elect_GWP = electricity_GWP(electricity_requirement_pelleting)

        # Add to GWP object
        GWP_object.add_subprocess(name="Electricity", GWP=elect_GWP)
        GWP_object.calculate_GWP_from_subprocesses()

        # Add to MC outputs object
        MC_outputs.add_GWP_object(GWP_object)

    # add abbreviations of subprocess'
    MC_outputs.subprocess_abbreviations = ("Elect.",)

    # Update toml document with average particle size after milling
    particle_size_post_pelleting_mm = 6.35  # [mm] source: "10.13031/aea.30.9719"
    update_user_inputs_toml("particle size after pelleting", float(particle_size_post_pelleting_mm))

    return MC_outputs
