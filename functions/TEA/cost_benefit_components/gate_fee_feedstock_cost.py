import functions
import objects

import numpy as np

from config import settings

def gate_fee_or_feedstock_cost_benefit():
    """
    Calculates benefits or costs resulting from gate fees received for treating a feedstock or from feedstock costs
    for buying a feedstock.

    Parameters
    ----------

    Returns
    -------
    AnnualValue
        Annual value/annuity object containing array of benefits (+ve) or costs (-ve) resulting from gate fees
        received for treating a feedstock or from feedstock costs for buying a feedstock.
        Returned as the currency defined in settings.user_inputs.general.currency.
    """

    # Get background data
    system_size_tonnes_per_hour = settings.user_inputs.system_size.mass_basis_tonnes_per_hour

    # Get annual operating hours
    if settings.user_inputs.general.annual_operating_hours_user_imputed:
        annual_operating_hours_array = functions.MonteCarloSimulation.to_fixed_MC_array(
            value=settings.user_inputs.general.annual_operating_hours)
    else:
        annual_operating_hours_array = np.array(functions.TEA.get_annual_operating_hours_draws())

    system_size_tonnes_per_year_array = system_size_tonnes_per_hour * annual_operating_hours_array

    # Get prices
    if settings.user_inputs.economic.gate_fee_or_feedstock_price_choice == "default":
        raise ValueError("Currently default values are not supported for gate fees/feedstock costs. Since these vary "
                         "too much based on the feedstock choice and regional conditions etc.")

    elif settings.user_inputs.economic.gate_fee_or_feedstock_price_choice == "user selected":
        price_distribution = functions.MonteCarloSimulation.dist_maker_from_settings(
            location=settings.user_inputs.economic.gate_fee_or_feedstock_price_parameters)  # currency/tonne feedstock

    else:
        raise ValueError("Gate fee or feedstock cost option not supported.")

    # Prices [currency/tonne feedstock]
    prices_array = functions.MonteCarloSimulation.get_distribution_draws(distribution_maker=price_distribution,
                                                                         length_array=len(annual_operating_hours_array))

    # Gate fee case (i.e. +ve cash flows)
    annuity_cash_flow_array = np.multiply(system_size_tonnes_per_year_array, prices_array)  # currency/year

    # Feedstock cost case (i.e. -ve cash flows)
    if settings.user_inputs.economic.gate_fee_or_feedstock_price_selection == "feedstock cost":
        annuity_cash_flow_array *= -1  # currency/year

    output_cost_benefit = objects.AnnualValue(values=list(annuity_cash_flow_array), name="biochar sale", short_label="BC")

    return output_cost_benefit
