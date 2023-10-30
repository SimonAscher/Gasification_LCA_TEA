import functions
import warnings

import numpy as np

from config import settings
from objects import AnnualValue, triangular_dist_maker


def carbon_capture_amine_consumption_cost_benefit(CO2_capture_rate):
    """
     Calculates costs/benefits due to amine (MEA) consumption for amine-based carbon capture process.

    Parameters
    ----------
    CO2_capture_rate: list[float]
        CO2 capture rate of system [kg CO2eq./tonne feedstock].

    Returns
    -------
    AnnualValue
        Annual value/annuity objects containing array of costs (-ve) or benefits (+ve) due to
        amine consumption.
        Returned as the currency defined in settings.user_inputs.general.currency.

    """
    # Check that right type of carbon capture process is defined in user inputs
    if settings.user_inputs.processes.carbon_capture.method != "Amine post comb":
        output_cost_benefit = AnnualValue(values=list(np.zeros(settings.user_inputs.general.MC_iterations)),
                                          name="Amine requirements for carbon capture",
                                          short_label="CC MEA")
        warnings.warn("Carbon capture process is not amine-based - hence not MEA should be consumed.")

    else:
        # Get system size
        system_size_tonnes_per_hour = settings.user_inputs.system_size.mass_basis_tonnes_per_hour

        # Get annual operating hours
        if settings.user_inputs.general.annual_operating_hours_user_imputed:
            annual_operating_hours_array = functions.MonteCarloSimulation.to_fixed_MC_array(
                value=settings.user_inputs.general.annual_operating_hours)
        else:
            annual_operating_hours_array = np.array(functions.TEA.get_annual_operating_hours_draws())

        system_size_tonnes_per_year_array = system_size_tonnes_per_hour * annual_operating_hours_array

        # Get flue gas available for capture
        # Convert from [kg CO2/FU] to [tonnes CO2/FU] i.e. [tonne CO2/tonne feedstock]
        flue_gas_CO2_array = list(np.divide(CO2_capture_rate, 1000))

        # Define MEA degradation rate and MEA price
        amine_degradation_rate = triangular_dist_maker(lower=0.3, mode=0.7, upper=2.2)  # [kg MEA/tonne CO2]
        amine_price = triangular_dist_maker(lower=0.90, mode=1.75, upper=2.50)  # [USD/kg MEA]

        # Update currency
        amine_price = triangular_dist_maker(lower=functions.TEA.convert_currency_annual_average(value=amine_price.lower,
                                                                                                year=settings.user_inputs.economic.CEPCI_year,
                                                                                                base_currency="USD",
                                                                                                converted_currency=settings.user_inputs.general.currency),
                                            mode=functions.TEA.convert_currency_annual_average(value=amine_price.mode,
                                                                                               year=settings.user_inputs.economic.CEPCI_year,
                                                                                               base_currency="USD",
                                                                                               converted_currency=settings.user_inputs.general.currency),
                                            upper=functions.TEA.convert_currency_annual_average(value=amine_price.upper,
                                                                                                year=settings.user_inputs.economic.CEPCI_year,
                                                                                                base_currency="USD",
                                                                                                converted_currency=settings.user_inputs.general.currency))  # [currency/kg MEA]

        amine_degradation_rate_array = functions.MonteCarloSimulation.get_distribution_draws(
            distribution_maker=amine_degradation_rate,
            length_array=len(flue_gas_CO2_array))  # [kg MEA/tonne CO2]

        amine_price_array = functions.MonteCarloSimulation.get_distribution_draws(
            distribution_maker=amine_price,
            length_array=len(flue_gas_CO2_array))  # [currency/kg MEA]

        # Calculate costs/benefits
        amine_consumption_per_FU = np.multiply(amine_degradation_rate_array, flue_gas_CO2_array)  # [kg MEA/FU]
        costs_benefits_amine_consumption_per_FU = np.multiply(amine_consumption_per_FU, amine_price_array)  # [currency/FU]

        # Convert per FU units to life cycle costs/benefits
        annuity_cash_flow_array_amine_consumption = (costs_benefits_amine_consumption_per_FU *
                                                     system_size_tonnes_per_year_array)  # [currency/year]

        # Get final annual value objects
        output_cost_benefit = AnnualValue(values=list(annuity_cash_flow_array_amine_consumption),
                                          name="Amine requirements for carbon capture",
                                          short_label="CC MEA",
                                          tag="Other operational expenses")

    return output_cost_benefit
