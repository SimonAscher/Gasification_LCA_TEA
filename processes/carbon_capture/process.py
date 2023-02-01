import numpy as np
from config import settings
from configs import process_GWP_output, process_GWP_output_MC
from processes.carbon_capture.utils import carbon_capture_VPSA_post_comb, carbon_capture_amine_post_comb
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from processes.syngas_combustion import syngas_combustion_GWP_MC
from functions.LCA import electricity_GWP, thermal_energy_GWP


def carbon_capture_GWP_MC(ML_predictions=None, syngas_combustion_outputs=None, cc_method="VPSA post combustion",
                          MC_iterations=settings.background.iterations_MC):
    """
    Calculate the GWP of carbon capture for all Monte Carlo runs.

    Parameters
    ----------
    ML_predictions: dict
        Dictionary of all predicted model outputs as distributions.
    syngas_combustion_outputs: object
        Syngas combustion sub model outputs.
    cc_method: str
        Specifies carbon capture method. "VPSA post combustion" by default. Alternatively "Amine post comb" or "VPSA pre combustion" (not yet supported).
    MC_iterations: int
        Number of Monte Carlo iterations.

    Returns
    -------

    """
    # Get defaults
    if ML_predictions is None:
        ML_predictions = get_all_prediction_distributions()
    if syngas_combustion_outputs is None:
        syngas_combustion_outputs = syngas_combustion_GWP_MC()

    # Initialise MC output object
    if cc_method == "VPSA pre combustion":
        name_process = "Carbon capture - VPSA pre comb."
    elif cc_method == "Amine post comb":
        name_process = "Carbon capture - Amine post comb."
    elif cc_method == "VPSA post combustion":  # default option
        name_process = "Carbon capture - VPSA post comb."
    else:
        raise ValueError("Carbon capture method not supported")

    # Initialise MC output object
    MC_outputs = process_GWP_output_MC(process_name="Carbon Capture")

    # Do analysis for post combustion process' which act on the flue gas
    if cc_method in ["Amine post comb", "VPSA post combustion"]:
        for _, count in enumerate(np.arange(len(syngas_combustion_outputs.simulation_results))):
            # Initialise GWP_object
            GWP_object = process_GWP_output(process_name=name_process)

            # Get carbon capture requirements and recovery rate based on selected process
            if cc_method == "Amine post comb":
                cc_reqs = carbon_capture_amine_post_comb()
            elif cc_method == "VPSA post combustion":  # default option
                cc_reqs = carbon_capture_VPSA_post_comb()

            # Calculate captured CO2 [kg CO2eq./FU]
            avoided_GWP = -1 * (syngas_combustion_outputs.simulation_results[count].GWP +
                                syngas_combustion_outputs.simulation_results[count].GWP_from_biogenic) * cc_reqs["Recovery"]
            elect_GWP = electricity_GWP(-1 * avoided_GWP * cc_reqs["Electricity consumption"])
            heat_GWP = thermal_energy_GWP(-1 * avoided_GWP * cc_reqs["Heat consumption"])

            # Add to GWP object
            GWP_object.add_subprocess(name="Captured CO2", GWP=avoided_GWP)
            GWP_object.add_subprocess(name="Electricity", GWP=elect_GWP)
            GWP_object.add_subprocess(name="Heat", GWP=heat_GWP)
            GWP_object.calculate_GWP_from_subprocesses()

            # Add to MC outputs object
            MC_outputs.add_GWP_object(GWP_object)

        # add abbreviations of subprocess'
        MC_outputs.subprocess_abbreviations = ("CC", "Elect.", "Heat",)

    # Do analysis for pre combustion process which acts on the syngas
    elif cc_method == "VPSA pre combustion":
        # Currently not included - would need to include a water gas shift rector to convert CO to CO2
        # (CO + H2O ⇌ CO2 + H2). From here could calculate syngas composition after shifting - apply capture and then
        # compare to conventional process. Look at syngas combustion model to see how to calculate GWP from syngas
        # combustion. Will have similar process here but with most CO2 already extracted.
        raise ValueError("Pre combustion carbon capture currently not supported as other methods deemed more suitable.")

    else:
        raise ValueError("Carbon capture method not supported")

    return MC_outputs
