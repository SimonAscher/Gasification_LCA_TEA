import functions

import numpy as np

from config import settings
from objects import triangular_dist_maker, AnnualValue


def oxygen_consumption_cost_benefit(unit_oxygen_requirement):
    """
     Calculates costs/benefits due to the consumption of pure (<90% purity) oxygen .

    Parameters
    ----------
    unit_oxygen_requirement: float
        Oxygen requirement [kg O2/kg feedstock wb] or [tonne O2/tonne feedstock wb].

    Returns
    -------
    AnnualValue
        Annual value/annuity objects containing array of costs (-ve) or benefits (+ve) due to
        amine consumption.
        Returned as the currency defined in settings.user_inputs.general.currency.

    """
    # Get system size
    system_size_tonnes_per_hour = settings.user_inputs.system_size.mass_basis_tonnes_per_hour  # [tonnes/hour]
    oxygen_requirement = unit_oxygen_requirement * system_size_tonnes_per_hour  # [tonne O2/hour]

    # Get annual oxygen requirement
    annual_operating_hours_array = functions.TEA.get_annual_operating_hours_draws()  # [hours/year]
    annual_oxygen_requirements_array = np.multiply(oxygen_requirement, annual_operating_hours_array)  # [tonne O2/year]

    # Set oxygen price
    oxygen_price = triangular_dist_maker(lower=30, mode=50, upper=70)  # [USD/tonne O2]

    # Update currency
    oxygen_price = triangular_dist_maker(lower=functions.TEA.convert_currency_annual_average(value=oxygen_price.lower,
                                                                                             year=settings.user_inputs.economic.CEPCI_year,
                                                                                             base_currency="USD",
                                                                                             converted_currency=settings.user_inputs.general.currency),
                                         mode=functions.TEA.convert_currency_annual_average(value=oxygen_price.mode,
                                                                                            year=settings.user_inputs.economic.CEPCI_year,
                                                                                            base_currency="USD",
                                                                                            converted_currency=settings.user_inputs.general.currency),
                                         upper=functions.TEA.convert_currency_annual_average(value=oxygen_price.upper,
                                                                                             year=settings.user_inputs.economic.CEPCI_year,
                                                                                             base_currency="USD",
                                                                                             converted_currency=settings.user_inputs.general.currency))  # [currency/tonne O2]

    # Get price draws
    oxygen_price_array = functions.MonteCarloSimulation.get_distribution_draws(distribution_maker=oxygen_price,
                                                                               length_array=settings.user_inputs.general.MC_iterations)  # [currency/tonne O2]

    # Convert per FU units to life cycle costs/benefits
    annuity_cash_flow_array_oxygen_consumption = np.multiply(annual_oxygen_requirements_array, oxygen_price_array)  # [currency/year]
    annuity_cash_flow_array_oxygen_consumption = np.multiply(annuity_cash_flow_array_oxygen_consumption, -1)  # Convert values to -ve as they are a cost

    # Get final annual value objects
    output_cost_benefit = AnnualValue(values=list(annuity_cash_flow_array_oxygen_consumption),
                                      name="Oxygen as gasifying agent",
                                      short_label="O2 Ag",
                                      tag="Other operational expenses")

    return output_cost_benefit
