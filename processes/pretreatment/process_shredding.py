import numpy as np

from config import settings
from configs import process_GWP_output, process_GWP_output_MC
from functions.LCA import electricity_GWP
from processes.pretreatment.utils import electricity_shredding


def shredding_GWP_MC(MC_iterations=settings.background.iterations_MC):
    """
    Calculate the GWP of feedstock bale shredding for all Monte Carlo runs.

    Parameters
    ----------
    MC_iterations: int
         Number of Monte Carlo iterations.

    Returns
    -------
    """

    # Initialise MC output object
    MC_outputs = process_GWP_output_MC(process_name="Shredding")

    # Do analysis
    for _, count in enumerate(np.arange(MC_iterations)):
        # Initialise GWP_object
        GWP_object = process_GWP_output(process_name="Shredding")

        # Calculate GWP
        electricity_requirement_shredding = electricity_shredding()
        elect_GWP = electricity_GWP(electricity_requirement_shredding)

        # Add to GWP object
        GWP_object.add_subprocess(name="Electricity", GWP=elect_GWP)
        GWP_object.calculate_GWP_from_subprocesses()

        # Add to MC outputs object
        MC_outputs.add_GWP_object(GWP_object)

    # Add abbreviations of subprocess'
    MC_outputs.subprocess_abbreviations = ("Elect.",)

    return MC_outputs
