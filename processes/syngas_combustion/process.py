import numpy as np
from config import settings
from functions.general.utility import scale_gas_fractions
from processes.syngas_combustion.utils import syngas_combustion_CO2_eq


def syngas_combustion_GWP(predictions):
    """
    Calculates the GWP of syngas combustion.

    Parameters
    ----------
    predictions: dict
        Dictionary of all predicted model outputs as distributions.

    FU: float
        Functional Unit used in analysis

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
    GWP_syngas_combustion = syngas_combustion_CO2_eq(scaled_gas_fractions, gas_yield)  # [kg CO2eq./FU]

    # Add output as biogenic/non-biogenic emissions
    biogenic_fraction = settings.data.biogenic_fractions[settings.user_inputs.feedstock_category]
    GWP_exc_biogenic = list(np.array(GWP_syngas_combustion) * (1 - biogenic_fraction))

    # TODO: I think GWP_exc_biogenic should be returned instead as first function return - do not consider biogenic
    #  emissions in analysis Return final calculated GWPs from syngas combustion
    return GWP_exc_biogenic, {"inc. biogenic GWP": GWP_syngas_combustion, "exc. biogenic GWP": GWP_exc_biogenic,
                              "units": "kg CO2eq./FU"}
