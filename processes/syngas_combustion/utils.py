import numpy as np

from config import settings


# Define helper functions
def get_molar_masses():
    """ Get molar mass data from settings."""
    return settings.data.molar_masses


def get_conversion_ratios_to_CO2():
    """
    Get conversion ratios from CO, CH4, C2H4 to CO2.

    Returns
    -------
    dict

    """
    # Get molar masses
    mm = get_molar_masses()

    # Calculate conversion ratios to CO2
    CO_conv_ratio = (2 * mm["CO2"]) / (2 * mm["CO"])  # 2 CO + O2 -> 2 CO2
    CH4_conv_ratio = (mm["CO2"]) / mm["CH4"]  # CH4 + 2O2 -> CO2 + 2 H2O
    C2H4_conv_ratio = (2 * mm["CO2"]) / mm["C2H4"]  # C2H4 + 3 O2 -> 2 CO2 + 2 H2O

    return {"CO": CO_conv_ratio, "CH4": CH4_conv_ratio, "C2H4": C2H4_conv_ratio}


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
    FU: int
        Functional unit.

    Returns
    -------
        GWP values in kg CO2eq./FU.
    """

    # Ensure inputs are the correct length
    if len(scaled_gas_fractions) != 6:
        raise ValueError(f"gas_fractions needs to be length 6, is {len(scaled_gas_fractions)}")

    # Set up empty list to store calculated GWPs
    GWP = []

    # Get gas conversion ratios
    conversion_ratios = get_conversion_ratios_to_CO2()
    CO_conv_ratio = conversion_ratios["CO"]
    CH4_conv_ratio = conversion_ratios["CH4"]
    C2H4_conv_ratio = conversion_ratios["C2H4"]

    # Get gas densities
    densities = settings.data.densities

    # Calculate GWPs for each MC iteration
    for iterations in np.arange(len(scaled_gas_fractions["N2 [vol.% db]"])):
        calculated_GWP = (scaled_gas_fractions["CO2 [vol.% db]"][iterations] * densities["CO2"] +
                          scaled_gas_fractions["CO [vol.% db]"][iterations] * densities["CO"] * CO_conv_ratio +
                          scaled_gas_fractions["CH4 [vol.% db]"][iterations] * densities["CH4"] * CH4_conv_ratio +
                          scaled_gas_fractions["C2Hn [vol.% db]"][iterations] * densities["C2H4"] * C2H4_conv_ratio
                          ) * gas_yield[iterations] * FU
        GWP.append(calculated_GWP)  # add GWP to storage list

    return GWP
