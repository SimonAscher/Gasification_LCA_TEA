import functions

import numpy as np

from config import settings
from objects import AnnualValue, range_dist_maker
from processes.carbon_capture.process import CarbonCapture


def get_carbon_capture_CAPEX_distribution(results, currency=None, CEPCI_year=None):
    """
    Calculate the CAPEX distribution of a carbon capture plant.
    CAPEX is given as total overnight cost (TOC) or total installed cost (TIC) (i.e. engineering works, procurement,
    installation, etc. are considered included in CAPEX).

    Parameters
    ----------
    results:
        Results object with CarbonCapture process.
    currency: str | None
        Currency that is to be used for analysis.
    CEPCI_year: int | None
        Reference CEPCI year that is to be used for analysis.

    Returns
    -------
    AnnualValue
        Distribution of CAPEX values in the supplied currency.

    """
    # Get defaults
    if currency is None:
        currency = settings.user_inputs.general.currency

    if CEPCI_year is None:
        CEPCI_year = settings.user_inputs.economic.CEPCI_year

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
    CCS_results = [process for process in results.processes if isinstance(process, CarbonCapture)][0]

    GWP_results_fossil_CO2 = CCS_results.GWP_results[0].values
    GWP_results_biogenic_CO2 = CCS_results.GWP_results[1].values
    flue_gas_CO2_array = list(np.add(GWP_results_fossil_CO2, GWP_results_biogenic_CO2) / 1000 * -1)
    # [tonne CO2/FU] i.e. [tonne CO2/tonne feedstock]
    # divide by 1000 to turn into tonnes and multiply by -1 to turn values positive

    # Capture only cost
    # Prices currency/tonne CO2
    baseline_price_capture_dist_USD_2008 = range_dist_maker(low=-50, high=-30)  # Note: Taken as -ve as it is a cost.
    updated_price_capture_dist_user_currency_2008 = range_dist_maker(
        low=functions.TEA.convert_currency_annual_average(value=baseline_price_capture_dist_USD_2008.low, year=2008,
                                                          base_currency="USD", converted_currency=currency),
        high=functions.TEA.convert_currency_annual_average(value=baseline_price_capture_dist_USD_2008.high, year=2008,
                                                           base_currency="USD", converted_currency=currency))
    price_distribution_capture = range_dist_maker(low=functions.TEA.CEPCI_scale(base_year=2008,
                                                                                design_year=CEPCI_year,
                                                                                value=updated_price_capture_dist_user_currency_2008.low),
                                                  high=functions.TEA.CEPCI_scale(base_year=2008,
                                                                                 design_year=CEPCI_year,
                                                                                 value=updated_price_capture_dist_user_currency_2008.high))  # [currency/ tonne CO2]

    prices_array_capture = functions.MonteCarloSimulation.get_distribution_draws(
        distribution_maker=price_distribution_capture,
        length_array=len(flue_gas_CO2_array))  # [currency/tonne CO2]

    costs_benefits_per_FU_capture = np.multiply(flue_gas_CO2_array, prices_array_capture)  # currency/FU

    # Convert per FU units to life cycle costs/benefits
    annuity_cash_flow_array_capture = costs_benefits_per_FU_capture * system_size_tonnes_per_year_array

    CAPEX = AnnualValue(values=list(annuity_cash_flow_array_capture),
                        name="Carbon Capture CAPEX",
                        short_label="CC")

    return CAPEX
