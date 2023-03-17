from config import settings
from configs import triangular_dist_maker, gaussian_dist_maker, fixed_dist_maker, range_dist_maker
from functions.general.utility import kJ_to_kWh, MJ_to_kWh
from functions.MonteCarloSimulation import get_distribution_draws
from functions.general.utility import user_input_to_dist_maker

def thermal_energy_cost_benefit(amount, source=None, units="kWh", country=settings.user_inputs.country,
                                displaced=False):
    pass


def electricity_cost_benefit(amount, source=None, price_distribution=user_input_to_dist_maker(settings.user_inputs.electricity_price), electricity_units="kWh",
                             country=settings.user_inputs.country, currency = settings.user_inputs.currency,
                             sold=False):
    """
     Function to determine the GWP of using (or avoiding) a certain amount of grid electricity.

     Parameters
     ----------
     amount: float
         Defines the amount of electricity used.
     source: str
         Defines which source is considered for electricity production.
    price_distribution: triangular_dist_maker | gaussian_dist_maker | fixed_dist_maker | range_dist_maker
        Named tuple defining the distribution which is to be used.
     electricity_units: str
         Defines units used in analysis - currently only kWh supported.
     country: str
         Specifies the reference country or region.
     used: bool
         Determines whether energy is sold to the grid or bought from the grid.
     Returns
     -------
     float
         GWP value in kg CO2eq.
     """

    # Get defaults
    if source is None:
        source = "grid"
    else:
        raise TypeError("Electricity source not supported.")

    if price_distribution is None:  # Default price distributions based on country
        if settings.user_inputs.country == "UK":
            data = settings.data.economic.electricity_wholesale_prices.most_recent.UK
            price_distribution = triangular_dist_maker(lower=data.lower, mode=data.mode, upper=data.upper)  # "GBP/kWh"

        elif settings.user_inputs.country == "USA":
            pass

        else:
            raise ValueError("Default electricity costs for this country are currently not supported.")

        # Check that units are compatible
        units = settings.data.economic.electricity_wholesale_prices.most_recent[settings.user_inputs.country].units
        if "kWh" not in units:
            raise ValueError("Incorrect units supplied. Should be given as kWh.")

        if currency not in units:
            raise ValueError("Incorrect currency supplied.")

    # Convert units if not kWh
    if electricity_units == "kWh":
        pass
    elif electricity_units == "kJ":
        amount = kJ_to_kWh(amount)
    elif electricity_units == "MJ":
        amount = MJ_to_kWh(amount)
    else:
        raise TypeError("Other units currently not supported.")

    # Calculate cost/benefit
    output_cost_benefit = amount * get_distribution_draws(distribution_maker=price_distribution, length_array=1)

    return output_cost_benefit
