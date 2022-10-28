import numpy as np
from config import settings

# Sub-function to calculate GWP of syngas combustion
def syngas_combustion_CO2_eq(scaled_gas_fractions, gas_yield, FU=settings.general["FU"]):
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
        GWP values in kg CO2eq./FU.
    """

    # Ensure inputs are the correct length
    if len(scaled_gas_fractions) != 6:
        raise ValueError(f"gas_fractions needs to be length 6, is {len(scaled_gas_fractions)}")

    # Set up empty list to store calculated GWPs
    GWP = []

    # Get gas molar masses
    mm = settings.data.molar_masses

    # TODO: CHECK ALL THESE EQUATIONS AND MAKE SURE THEY ARE BALANCED AND THE CORRESPONDING RATIOS ARE CORRECT - WRITE TESTS
    # Calculate conversion ratios to CO2
    CO_conv_ratio = (2 * mm["CO2"]) / (2 * mm["CO"])  # 2 CO + O2 -> 2 CO2
    CH4_conv_ratio = (mm["CO2"]) / mm["CH4"]  # CH4 + 2O2 -> CO2 + 2 H2O
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
