import numpy as np

from config import settings
from functions.general.utility import scale_gas_fractions


def syngas_combustion_GWP(predictions, FU=settings.general["FU"]):
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

    # Create and employ sub-function to calculate GWP of syngas combustion
    def syngas_combustion_CO2_eq(scaled_gas_fractions, gas_yield):
        """
        Sub-function used to calculate the GWP from syngas combustion.
        Simplified function assuming complete conversion of all species to CO2 are employed.

        Parameters
        ----------
        scaled_gas_fractions: dict
            Scaled gas fraction in decimals.
        gas_yield: list
            Gas yields associated with each iteration.

        Returns
        -------
        list
            GWP values in kg CO2eq. / FU.
        """

        # Ensure inputs are the correct length
        if len(scaled_gas_fractions) != 6:
            raise ValueError(f"gas_fractions needs to be length 6, is {len(scaled_gas_fractions)}")

        # Set up empty list to store calculated GWPs
        GWP = []

        # Get gas molar masses
        mm = settings.data.molar_masses

        # Calculate conversion ratios to CO2
        CO_conv_ratio = (2 * mm["CO2"]) / (2 * mm["CO"])  # 2 CO + O2 -> 2 CO2
        CH4_conv_ratio = (2 * mm["CO2"]) / mm["CH4"]  # CH4 + 2O2 -> 2 CO2
        C2H4_conv_ratio = (2 * mm["CO2"]) / mm["C2H4"]  # C2H4 + 3 O2 -> 2 CO2 + 2 H2O

        # Calculate GWPs for each MC iteration
        for iterations in np.arange(len(scaled_gas_fractions["N2 [vol.% db]"])):
            calculated_GWP = (scaled_gas_fractions["CO2 [vol.% db]"][iterations] +
                              scaled_gas_fractions["CO [vol.% db]"][iterations] * CO_conv_ratio +
                              scaled_gas_fractions["CH4 [vol.% db]"][iterations] * CH4_conv_ratio +
                              scaled_gas_fractions["C2Hn [vol.% db]"][iterations] * C2H4_conv_ratio
                              ) * gas_yield[iterations] * settings.data.densities["CO2"] * FU
            GWP.append(calculated_GWP)  # add GWP to storage list
            # TODO: Add case where only 1 set of predictions is given instead of distributions - just in case this is
            #  needed.

        return GWP

    # Employ GWP calculation function
    GWP_syngas_combustion = syngas_combustion_CO2_eq(scaled_gas_fractions, gas_yield)  # [kg CO2eq. / FU]

    # Add output as biogenic/non-biogenic emissions
    biogenic_fraction = settings.data.biogenic_fractions[settings.user_inputs.feedstock_category]
    GWP_biogenic = list(np.array(GWP_syngas_combustion) * biogenic_fraction)
    GWP_non_biogenic = list(np.array(GWP_syngas_combustion) * (1 - biogenic_fraction))

    # Return final calculated GWPs from syngas combustion
    return GWP_syngas_combustion, {"biogenic GWP": GWP_biogenic, "non-biogenic GWP": GWP_non_biogenic}
