import functions
import numpy as np

from config import settings


def heat_cost_benefit(heat_array):
    """
    Applies electricity price to an array of electricity requirements (i.e. generation or consumption).

    Parameters
    ----------
    heat_array: ArrayLike
        List or array of heat requirements in [kWh] or [kWh/FU].

    Returns
    -------
    ArrayLike
        Array of costs (-ve) or benefits (+ve) per FU resulting from the corresponding requirement.
        Returned as the currency defined in settings.user_inputs.general.currency.
    """

    # Check how heat price is defined and get corresponding price distribution
    if settings.user_inputs.economic.heat_price_choice == "default" and settings.user_inputs.reference_energy_sources.heat == "natural gas":
        price_distribution = functions.MonteCarloSimulation.dist_maker_from_settings(
            location=settings.data.economic.natural_gas_price[settings.user_inputs.general.country])

        prices = functions.MonteCarloSimulation.get_distribution_draws(distribution_maker=price_distribution,
                                                                       length_array=len(heat_array))
        # Convert prices from thm to kWh if necessary
        if settings.data.economic.natural_gas_price[settings.user_inputs.general.country].units.split("/")[1]:
            prices = functions.general.utility.therm_to_kWh(np.array(prices), reverse=True)

        costs_benefits = np.multiply(heat_array, prices)
        costs_benefits = list(costs_benefits / 0.9)  # scale due to inefficiencies in conversion to heat

        # Check if currencies match up
        if settings.user_inputs.general.currency != \
                settings.data.economic.natural_gas_price[settings.user_inputs.general.country].units.split("/")[0]:
            raise ValueError("Heat price is in a different currency to the one supplied by the user.")

    elif settings.user_inputs.economic.heat_price_choice == "user selected":
        price_distribution = functions.MonteCarloSimulation.dist_maker_from_settings(
            location=settings.user_inputs.economic.heat_price_parameters)

        prices = functions.MonteCarloSimulation.get_distribution_draws(distribution_maker=price_distribution,
                                                                       length_array=len(heat_array))

        costs_benefits = list(np.multiply(heat_array, prices))

    else:
        raise ValueError("Heat price option not supported.")

    return costs_benefits


def electricity_cost_benefit(electricity_array):
    """
    Applies electricity price to an array of electricity requirements (i.e. generation or consumption).

    Parameters
    ----------
    electricity_array: ArrayLike
        List or array of electricity requirements in [kWh].

    Returns
    -------
    ArrayLike
        Array of costs (-ve) or benefits (+ve) per FU resulting from the corresponding requirement.
        Returned as the currency defined in settings.user_inputs.general.currency.
    """

    # Check how electricity price is defined and get corresponding price distribution
    if settings.user_inputs.economic.electricity_price_choice == "default":
        price_distribution = functions.MonteCarloSimulation.dist_maker_from_settings(
            location=settings.data.economic.electricity_wholesale_prices[settings.user_inputs.general.country])

        # Check if currencies match up
        if settings.user_inputs.general.currency != settings.data.economic.electricity_wholesale_prices[
            settings.user_inputs.general.country].units.split("/")[0]:
            raise ValueError("Electricity price is in a different currency to the one supplied by the user.")

    elif settings.user_inputs.economic.electricity_price_choice == "user selected":
        price_distribution = functions.MonteCarloSimulation.dist_maker_from_settings(
            location=settings.user_inputs.economic.electricity_price_parameters)

    else:
        raise ValueError("Electricity price option not supported.")

    prices = functions.MonteCarloSimulation.get_distribution_draws(distribution_maker=price_distribution,
                                                                   length_array=len(electricity_array))

    costs_benefits = list(np.multiply(electricity_array, prices))

    return costs_benefits
