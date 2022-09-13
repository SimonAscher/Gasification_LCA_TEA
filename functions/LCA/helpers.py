from config import settings

def get_CO2_equ(*,CO2: float = 0, CH4_fossil: float = 0, CH4_non_fossil: float = 0, N2O: float = 0) -> float:
    """
    Convert CO2, CH4, and N2O emissions to their CO2-eq. emissions.

    Parameters
    ----------
    CO2: float
    CH4_fossil: float
    CH4_non_fossil: float
    N2O: float

    Returns
    -------
    float
        Carbon dioxide equivalent emissions

    .. note::
    Ensure all inputs have the same units. Function will return the GWP in the same units.
    """

    from config import settings
    CO2_equ_factor = settings.data.CO2_equivalents.CO2_equ_factor
    CH4_fossil_equ_factor = settings.data.CO2_equivalents.CH4_fossil_equ_factor
    CH4_non_fossil_equ_factor = settings.data.CO2_equivalents.CH4_non_fossil_equ_factor
    N2O_equ_factor = settings.data.CO2_equivalents.N2O_equ_factor

    # Calculate GWP of process
    GWP = (CO2 * CO2_equ_factor + CH4_fossil * CH4_fossil_equ_factor + CH4_non_fossil * CH4_non_fossil_equ_factor
           + N2O * N2O_equ_factor)

    return GWP

def natural_gas_for_heat_GWP(heat, units = "kWh"):
    """
    Function which calculates the GWP of requiring X natural gas for heating purposes.
    Note inefficiencies etc. already taken into account elsewhere.

    Parameters
    ----------
    heat: float
        Amount of natural gas used for heat generation.
    units: str
        Defines units used in analysis - either kWh or kJ

    Returns
    -------

    """
    carbon_intensity_natural_gas = settings.data.CO2_equivalents.natural_gas_for_heat[settings.user_inputs.country]

    # Convert to kJ in case that is used as unit
    if units == "kJ":
        heat = heat / 3600
        carbon_intensity_natural_gas = carbon_intensity_natural_gas / 3600

    GWP = carbon_intensity_natural_gas * heat

    return GWP


