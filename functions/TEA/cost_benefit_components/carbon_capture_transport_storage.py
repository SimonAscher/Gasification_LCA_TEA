import functions

import numpy as np

from config import settings
from objects import AnnualValue, triangular_dist_maker


def carbon_capture_transport_storage_cost_benefit(CO2_capture_rate):
    """
    Calculates costs/benefits due to transport and storage part of carbon capture and storage (CCS) process.

    Parameters
    ----------
    CO2_capture_rate: list[float]
        CO2 capture rate of system [kg CO2eq./tonne feedstock].
    Returns
    -------
    tuple[AnnualValue, AnnualValue]
        Annual value/annuity objects containing array of costs (-ve) or benefits (+ve) due to
        carbon transport (1st tuple entry) and storage (2nd tuple entry).
        Returned as the currency defined in settings.user_inputs.general.currency.

    """
    # Get system size
    system_size_tonnes_per_hour = settings.user_inputs.system_size.mass_basis_tonnes_per_hour

    # Get annual operating hours
    if settings.user_inputs.general.annual_operating_hours_user_imputed:
        annual_operating_hours_array = functions.MonteCarloSimulation.to_fixed_MC_array(value=settings.user_inputs.general.annual_operating_hours)
    else:
        annual_operating_hours_array = np.array(functions.TEA.get_annual_operating_hours_draws())

    system_size_tonnes_per_year_array = system_size_tonnes_per_hour * annual_operating_hours_array

    # Get flue gas available for capture
    # Convert from [kg CO2/FU] to [tonnes CO2/FU] i.e. [tonne CO2/tonne feedstock]
    flue_gas_CO2_array = list(np.divide(CO2_capture_rate, 1000))

    # Get CO2 transport prices [currency/tonne CO2]
    if settings.user_inputs.economic.CO2_transport_price_choice == "default":
        baseline_price_transport = triangular_dist_maker(lower=2, mode=5, upper=15)  # [USD/tonne CO2]
        # Convert distributions to currency used in analysis.
        price_transport = triangular_dist_maker(
            lower=functions.TEA.convert_currency_annual_average(value=baseline_price_transport.lower, year=2022,
                                                                base_currency="USD",
                                                                converted_currency=settings.user_inputs.general.currency),
            mode=functions.TEA.convert_currency_annual_average(value=baseline_price_transport.mode, year=2022,
                                                               base_currency="USD",
                                                               converted_currency=settings.user_inputs.general.currency),
            upper=functions.TEA.convert_currency_annual_average(value=baseline_price_transport.upper, year=2022,
                                                                base_currency="USD",
                                                                converted_currency=settings.user_inputs.general.currency))
        # Get distribution draws
        price_array_transport = functions.MonteCarloSimulation.get_distribution_draws(
            distribution_maker=price_transport,
            length_array=len(flue_gas_CO2_array))  # [currency/tonne CO2]

    elif settings.user_inputs.economic.CO2_transport_price_choice == "user selected":
        price_array_transport = functions.MonteCarloSimulation.dist_maker_from_settings(
            location=settings.user_inputs.economic.CO2_transport_price_parameters)  # [currency/tonne CO2]

    else:
        raise ValueError("Carbon transport cost option not supported.")

    # Get CO2 storage prices [currency/tonne CO2]
    if settings.user_inputs.economic.CO2_storage_price_choice == "default":
        baseline_price_storage = triangular_dist_maker(lower=2, mode=10, upper=20)  # [USD/tonne CO2]
        # Convert distributions to currency used in analysis.
        price_storage = triangular_dist_maker(
            lower=functions.TEA.convert_currency_annual_average(value=baseline_price_storage.lower, year=2022,
                                                                base_currency="USD",
                                                                converted_currency=settings.user_inputs.general.currency),
            mode=functions.TEA.convert_currency_annual_average(value=baseline_price_storage.mode, year=2022,
                                                               base_currency="USD",
                                                               converted_currency=settings.user_inputs.general.currency),
            upper=functions.TEA.convert_currency_annual_average(value=baseline_price_storage.upper, year=2022,
                                                                base_currency="USD",
                                                                converted_currency=settings.user_inputs.general.currency))
        # Get distribution draws
        price_array_storage = functions.MonteCarloSimulation.get_distribution_draws(
            distribution_maker=price_storage,
            length_array=len(flue_gas_CO2_array))  # [currency/tonne CO2]

    elif settings.user_inputs.economic.CO2_storage_price_choice == "user selected":
        price_array_storage = functions.MonteCarloSimulation.dist_maker_from_settings(
            location=settings.user_inputs.economic.CO2_storage_price_parameters)  # [currency/tonne CO2]

    else:
        raise ValueError("Carbon storage cost option not supported.")

    # Calculate costs/benefits
    costs_benefits_per_FU_transport = np.multiply(flue_gas_CO2_array, price_array_transport)  # currency/FU
    costs_benefits_per_FU_storage = np.multiply(flue_gas_CO2_array, price_array_storage)  # currency/FU

    # Convert per FU units to life cycle costs/benefits
    annuity_cash_flow_array_transport = costs_benefits_per_FU_transport * system_size_tonnes_per_year_array
    annuity_cash_flow_array_storage = costs_benefits_per_FU_storage * system_size_tonnes_per_year_array

    # Get final annual value objects
    output_cost_benefit_transport = AnnualValue(values=list(annuity_cash_flow_array_transport),
                                                name="CO2 transport cost",
                                                short_label="CO2-T",
                                                tag="Other operational expenses")
    output_cost_benefit_storage = AnnualValue(values=list(annuity_cash_flow_array_storage),
                                              name="CO2 storage cost",
                                              short_label="CO2-S",
                                              tag="Other operational expenses")

    return output_cost_benefit_transport, output_cost_benefit_storage
