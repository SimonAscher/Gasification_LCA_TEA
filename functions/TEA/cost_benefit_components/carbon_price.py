import functions
import numpy as np

from config import settings
from objects import AnnualValue


def carbon_price_cost_benefit(results):
    """
    Calculates costs/benefits due to a carbon price which could be the result of an emissions trading scheme,
    a carbon tax, or a voluntary carbon market etc. The systems global net CO2eq. emissions are used.

    Parameters
    ----------
    results:
        Results object with calculated GWP.

    Returns
    -------
    AnnualValue
        Annual value/annuity object containing array of costs (-ve) or benefits (+ve) due to carbon tax.
        Returned as the currency defined in settings.user_inputs.general.currency.
    """

    # Get background data
    # Get GWP
    GWP_tonnes_per_FU = np.array(results.GWP_total) / 1000  # tonnes CO2eq./FU

    # Get system size
    system_size_tonnes_per_hour = settings.user_inputs.system_size.mass_basis_tonnes_per_hour

    # Get annual operating hours
    if settings.user_inputs.general.annual_operating_hours_user_imputed:
        annual_operating_hours_array = functions.MonteCarloSimulation.to_fixed_MC_array(
            value=settings.user_inputs.general.annual_operating_hours)
    else:
        annual_operating_hours_array = np.array(functions.TEA.get_annual_operating_hours_draws())

    system_size_tonnes_per_year_array = system_size_tonnes_per_hour * annual_operating_hours_array

    # Check if a carbon tax is to be included
    if settings.user_inputs.economic.carbon_tax_included:

        if settings.user_inputs.economic.carbon_tax_choice == "default":
            price_distribution = functions.MonteCarloSimulation.dist_maker_from_settings(
                location=settings.data.economic.carbon_price[settings.user_inputs.general.country])  # [currency/tonne]

            # Check if currencies match up
            if settings.user_inputs.general.currency != settings.data.economic.carbon_price[settings.user_inputs.general.country].units.split("/")[0]:
                raise ValueError("Carbon price is in a different currency to the one supplied by the user.")
            pass

        elif settings.user_inputs.economic.carbon_tax_choice == "user selected":
            price_distribution = functions.MonteCarloSimulation.dist_maker_from_settings(
                location=settings.user_inputs.economic.carbon_tax_parameters)  # currency/tonne CO2eq.

        else:
            raise ValueError("Carbon tax price option not supported.")

        # Prices currency/tonne CO2eq.
        prices_array = functions.MonteCarloSimulation.get_distribution_draws(distribution_maker=price_distribution,
                                                                             length_array=len(GWP_tonnes_per_FU))

        costs_benefits_per_FU = np.multiply(GWP_tonnes_per_FU, prices_array)  # currency/FU
        costs_benefits_per_FU *= -1  # turn prices negative - i.e. neg. carbon emissions would lead to pos. cash flow
    else:  # no carbon tax case
        costs_benefits_per_FU = np.zeros(len(GWP_tonnes_per_FU))

    # Convert per FU units to life cycle costs/benefits
    annuity_cash_flow_array = costs_benefits_per_FU * system_size_tonnes_per_year_array

    output_cost_benefit = AnnualValue(values=list(annuity_cash_flow_array), name="carbon tax", short_label="CT")

    return output_cost_benefit
