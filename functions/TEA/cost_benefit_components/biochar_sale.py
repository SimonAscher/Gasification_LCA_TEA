import functions
import objects

import numpy as np

from config import settings


def biochar_sale_cost_benefit():
    """
    Calculates benefits (or costs) resulting from the sale of biochar.

    Parameters
    ----------

    Returns
    -------
    AnnualValue
        Annual value/annuity object containing array of benefits (+ve) (or costs (-ve)) due to the sale of biochar.
        Returned as the currency defined in settings.user_inputs.general.currency.
    """

    # Get biochar production
    biochar_yield_predictions = functions.general.predictions_to_distributions.get_all_prediction_distributions()["Char yield [g/kg wb]"]  # [kg/tonne feedstock]

    # Calculate biochar yield
    biochar_yield_array = (np.array(biochar_yield_predictions) / 1000)  # [tonnes biochar/tonne feedstock]

    # Get prices
    if settings.user_inputs.economic.biochar_price_choice == "default":
        price_distribution = functions.MonteCarloSimulation.dist_maker_from_settings(
            location=settings.data.economic.biochar_price[settings.user_inputs.general.country])  # [currency/tonne]

        # Check if currencies match up
        if settings.user_inputs.general.currency != settings.data.economic.biochar_price[settings.user_inputs.general.country].units.split("/")[0]:
            raise ValueError("Biochar price is in a different currency to the one supplied by the user.")

    elif settings.user_inputs.economic.biochar_price_choice == "user selected":
        price_distribution = functions.MonteCarloSimulation.dist_maker_from_settings(
            location=settings.user_inputs.economic.biochar_price_parameters)  # [currency/tonne biochar]

    else:
        raise ValueError("Biochar price option not supported.")

    # Prices [currency/tonne biochar]
    prices_array = functions.MonteCarloSimulation.get_distribution_draws(distribution_maker=price_distribution,
                                                                         length_array=len(biochar_yield_array))

    costs_benefits_per_FU = np.multiply(biochar_yield_array, prices_array)  # currency/FU

    # Convert per FU units to life cycle costs/benefits

    # Get background data
    system_size_tonnes_per_hour = settings.user_inputs.system_size.mass_basis_tonnes_per_hour

    # Get annual operating hours
    if settings.user_inputs.general.annual_operating_hours_user_imputed:
        annual_operating_hours_array = functions.MonteCarloSimulation.to_fixed_MC_array(
            value=settings.user_inputs.general.annual_operating_hours)
    else:
        annual_operating_hours_array = np.array(functions.TEA.get_annual_operating_hours_draws())

    system_size_tonnes_per_year_array = system_size_tonnes_per_hour * annual_operating_hours_array

    annuity_cash_flow_array = costs_benefits_per_FU * system_size_tonnes_per_year_array

    output_cost_benefit = objects.AnnualValue(values=list(annuity_cash_flow_array),
                                              name="biochar sale",
                                              short_label="BC")

    return output_cost_benefit
