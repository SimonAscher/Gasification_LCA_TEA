import numpy as np
from config import settings
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from functions.general.utility import scale_gas_fractions
from processes.syngas_combustion.utils import syngas_combustion_CO2_eq
from configs import process_GWP_output, process_GWP_output_MC


def syngas_combustion_GWP_MC(predictions=get_all_prediction_distributions()):
    """
    Calculates the GWP of syngas combustion.
    Note: Currently no function to calculate the GWP of an individual simulation exists for this process.

    Parameters
    ----------
    predictions: dict
        Dictionary of all predicted model outputs as distributions.

    Returns
    -------
    list
        List the length of MC iterations with GWP values.
    """

    # Extract gas_yield for later use
    gas_yield = predictions["Gas yield [Nm3/kg wb]"]

    # Create dictionary of gas species only
    gas_fractions = predictions.copy()

    # Drop unrequired variables if they exist in dictionary:
    if "LHV [MJ/Nm3]" in gas_fractions:
        gas_fractions.pop("LHV [MJ/Nm3]")
    if "Gas yield [Nm3/kg wb]" in gas_fractions:
        gas_fractions.pop("Gas yield [Nm3/kg wb]")
    if "Tar [g/Nm3]" in gas_fractions:
        gas_fractions.pop("Tar [g/Nm3]")
    if "Char yield [g/kg wb]" in gas_fractions:
        gas_fractions.pop("Char yield [g/kg wb]")

    # Scale gas fractions, so that they all sum up to 1. Turn from percentages to decimals.
    scaled_gas_fractions = scale_gas_fractions(gas_fractions, gas_fractions_format="percentages")

    # Employ GWP calculation function
    GWP_syngas_combustion_inc_biogenic = syngas_combustion_CO2_eq(scaled_gas_fractions, gas_yield)  # [kg CO2eq./FU]

    # Calculate non biogenic emission
    biogenic_fraction = settings.data.biogenic_fractions[settings.user_inputs.feedstock_category]
    GWP_syngas_combustion_exc_biogenic = list(np.array(GWP_syngas_combustion_inc_biogenic) * (1 - biogenic_fraction))

    # Initialise MC output object
    name_process = "Syngas combustion"
    MC_outputs = process_GWP_output_MC(process_name=name_process)

    # Store values in default MC output object
    for count, entry in enumerate(GWP_syngas_combustion_exc_biogenic):
        GWP_object = process_GWP_output(process_name=name_process, GWP=entry,
                                        GWP_inc_biogenic=GWP_syngas_combustion_inc_biogenic[count])
        GWP_object.add_subprocess(name=name_process, GWP=entry)
        MC_outputs.add_GWP_object(GWP_object)

    MC_outputs.subprocess_abbreviations = ("Syn. comb.", )  # add abbreviation of subprocess


    return MC_outputs
