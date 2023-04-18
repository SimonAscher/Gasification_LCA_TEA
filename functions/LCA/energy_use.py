from config import settings
from functions.general.utility import kJ_to_kWh, MJ_to_kWh


def thermal_energy_GWP(amount, source=None, units="kWh", country=None, displaced=False):
    """
    Function which calculates the GWP of thermal energy use.

    Parameters
    ----------
    amount: float
        Defines the amount of thermal energy used.
    source: str
        Defines which source is considered for heat production.
    units: str
        Defines units used in analysis - either kWh or kJ or MJ.
    country: str
        Reference country used in process.
    displaced: bool
        Determines whether energy is used (False) or displaces grid use (True).
    Returns
    -------
    float
        GWP value in kg CO2eq.
    """
    # Load defaults
    if source is None:
        source = "natural gas"

    if country is None:
        country = settings.user_inputs.general.country

    # Get country specific carbon intensity of thermal energy
    if source == "natural gas":
        carbon_intensity_natural_gas = settings.data.CO2_equivalents.thermal_energy.natural_gas[country]
    else:
        raise TypeError("Heat source not supported.")

    # Convert units if not kWh
    if units == "kWh":
        pass
    elif units == "kJ":
        amount = kJ_to_kWh(amount)
    elif units == "MJ":
        amount = MJ_to_kWh(amount)
    else:
        raise TypeError("Other units currently not supported.")

    # Calculate GWP value
    GWP = carbon_intensity_natural_gas * amount

    # Check if energy used or displaced
    if displaced:
        GWP *= -1

    return GWP


def electricity_GWP(amount, source=None, units="kWh", country=None, displaced=False):
    """
    Function to determine the GWP of using (or avoiding) a certain amount of grid electricity.

    Parameters
    ----------
    amount: float
        Defines the amount of electricity used.
    source: str
        Defines which source is considered for electricity production.
    units: str
        Defines units used in analysis - either kWh or kJ or MJ.
    country: str
        Specifies the reference country or region.
    displaced: bool
        Determines whether energy is used (False) or displaced (True).
    Returns
    -------
    float
        GWP value in kg CO2eq.
    """

    # Get defaults
    if source is None:
        source = "grid"

    if country is None:
        country = settings.user_inputs.general.country

    # Convert units if not kWh
    if units == "kWh":
        pass
    elif units == "kJ":
        amount = kJ_to_kWh(amount)
    elif units == "MJ":
        amount = MJ_to_kWh(amount)
    else:
        raise TypeError("Other units currently not supported.")

    # Calculate GWP value
    if source == "grid":
        electricity_intensity = settings.data.CO2_equivalents.electricity[country]
        GWP = electricity_intensity * amount
    else:
        raise TypeError("Electricity source not supported.")

    # Check if energy used or displaced
    if displaced:
        GWP *= -1

    return GWP
