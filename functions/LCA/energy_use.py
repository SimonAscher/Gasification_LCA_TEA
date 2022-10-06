from config import settings


def thermal_energy_GWP(amount, source="natural gas", units="kWh", country=settings.user_inputs.country):
    """
    Function which calculates the GWP of thermal energy use.

    Parameters
    ----------
    amount: float
        Defines the amount of thermal energy used.
    source: str
        Defines which source is considered for heat production.
    units: str
        Defines units used in analysis - either kWh or kJ or MJ
    country: str
        Reference country used in process.
    Returns
    -------
    float
        GWP value in kg CO2eq.
    """
    # Get country specific carbon intensity of thermal energy
    if source == "natural gas":
        carbon_intensity_natural_gas = settings.data.CO2_equivalents.thermal_energy.natural_gas[settings.user_inputs.country]
    else:
        raise TypeError("Heat source not supported.")

    # Convert units if not kWh
    if units == "kJ":
        amount = amount / 3600
        carbon_intensity_natural_gas = carbon_intensity_natural_gas / 3600

    elif units == "MJ":
        amount = amount / 3.6
        carbon_intensity_natural_gas = carbon_intensity_natural_gas / 3.6

    # Calculate GWP value
    GWP = carbon_intensity_natural_gas * amount

    return GWP


def electricity_GWP(amount, country=settings.user_inputs.country):
    """
    Function to determine the GWP of using (or avoiding) a certain amount of grid electricity.

    Parameters
    ----------
    amount: float
        Takes the amount of electricity in kWh.
    country: str
        Specifies the reference country or region.
    Returns
    -------
    float
        GWP value in kg CO2eq.
    """
    electricity_intensity = settings.data.CO2_equivalents.electricity[country]
    GWP = electricity_intensity * amount

    return GWP
