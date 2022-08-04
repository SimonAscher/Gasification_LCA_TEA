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
    Factors are based on the IPCC Sixth Assessment Report (AR6) and are for a 100-year time horizon
    """

    CO2_equ_factor = 1
    CH4_fossil_equ_factor = 29.8
    CH4_non_fossil_equ_factor = 27.2
    N2O_equ_factor = 273

    # Calculate GWP of process
    GWP = (CO2 * CO2_equ_factor + CH4_fossil * CH4_fossil_equ_factor + CH4_non_fossil * CH4_non_fossil_equ_factor
           + N2O * N2O_equ_factor)

    return GWP
