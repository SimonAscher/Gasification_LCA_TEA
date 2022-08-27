import numpy as np
from config import settings
from functions.general.utility import scale_gas_fractions


def syngas_combustion_GWP(predictions):
    """
    Calculates the GWP of syngas combustion.

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

    # Scale gas fractions so they all sum up to 100%
    scaled_gas_fractions = scale_gas_fractions(gas_fractions)

    # Create and employ sub-function to calculate GWP of syngas combustion
    def syngas_combustion_CO2_eq(scaled_gas_fractions, gas_yield):
        """
        Sub-function used to calculate the GWP from syngas combustion.
        Simplified function assuming complete conversion of all species to CO2.
        """

        # Set up empty list to store calculated GWPs
        GWP = []

        # Get gas densities
        densities = settings.data.densities

        # Calculate GWPs for each MC iteration
        for iterations in np.arange(len(gas_fractions['N2 [vol.% db]'])):
            calculated_GWP = (scaled_gas_fractions['CO2 [vol.% db]'][iterations] +
                              scaled_gas_fractions['CO [vol.% db]'][iterations] * (densities['CO2'] / densities['CO']) +
                              scaled_gas_fractions['CH4 [vol.% db]'][iterations] * (
                                          densities['CO2'] / densities['CH4']) +
                              scaled_gas_fractions['C2Hn [vol.% db]'][iterations] * (
                                          densities['CO2'] / densities['C2H4'])) * \
                             gas_yield[iterations]
            GWP.append(calculated_GWP)  # add GWP to storage list
            # TODO: Add case where only 1 set of predictions is given instead of distributions - just in case this is
            # needed.

        return GWP

    # Employ GWP calculation function
    GWP_syngas_combustion = syngas_combustion_CO2_eq(scaled_gas_fractions, gas_yield)  # [kg CO2 per kg feedstock in]

    # Return final calculated GWPs from syngas combustion
    return GWP_syngas_combustion
