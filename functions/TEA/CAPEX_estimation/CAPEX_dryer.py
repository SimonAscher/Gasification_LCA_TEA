import functions

from config import settings
from objects import PresentValue


def get_dryer_CAPEX_distribution(currency=None, CEPCI_year=None):
    """
    Calculate the CAPEX distribution of a dryer for feedstock drying.
    CAPEX is given as total overnight cost (TOC) or total installed cost (TIC) (i.e. engineering works, procurement,
    installation, etc. are considered included in CAPEX).

    Parameters
    ----------
    currency: str | None
        Currency that is to be used for analysis.
    CEPCI_year: int | None
        Reference CEPCI year that is to be used for analysis.

    Returns
    -------
    PresentValue
        Present value object containing distribution of CAPEX values in the supplied currency.
    """

    # Get default inputs
    if currency is None:
        currency = settings.user_inputs.general.currency

    if CEPCI_year is None:
        CEPCI_year = settings.user_inputs.economic.CEPCI_year

    # Get other defaults
    mass_feedstock = settings.general.FU  # i.e. 1000 kg
    moisture_ar = settings.user_inputs.feedstock.moisture_ar
    moisture_post_drying = settings.user_inputs.feedstock.moisture_post_drying

    # Check for erroneous inputs
    if moisture_ar < 1 or moisture_post_drying < 1:
        raise ValueError("Ensure that moisture contents are given as percentages.")
    if moisture_ar < moisture_post_drying:
        raise ValueError("Warning: Moisture content of as received feedstock must be higher than moisture content "
                         "post drying.")

    # Turn moisture's from percentages to decimals
    moisture_ar /= 100
    moisture_post_drying /= 100

    # Calculate mass of evaporated water:
    mass_water_initial = mass_feedstock * moisture_ar
    mass_feed_dry = mass_feedstock * (1 - moisture_ar)
    mass_water_post_drying = (mass_feed_dry * moisture_post_drying) / (1 - moisture_post_drying)
    mass_evaporated_water_per_FU = mass_water_initial - mass_water_post_drying  # [kg/FU]

    # Get system size
    system_size_tonnes_per_hour = settings.user_inputs.system_size.mass_basis_tonnes_per_hour  # [tonnes/hour]
    mass_evaporated_water_per_hour = mass_evaporated_water_per_FU * system_size_tonnes_per_hour  # [kg H2O/hour]

    # Reference system
    CEPCI_baseline_year = 2000
    baseline_CAPEX_2000_USD = -230000 * 2.4 * 4.4  # [USD]
    baseline_size = 700  # [kg H2O/hour]
    reference_scaling_factor = 0.65

    # Update CAPEX
    baseline_CAPEX_2000_currency = functions.TEA.convert_currency_annual_average(value=baseline_CAPEX_2000_USD,
                                                                                 year=CEPCI_baseline_year,
                                                                                 base_currency="USD",
                                                                                 converted_currency=currency)

    baseline_CAPEX_updated_year_and_currency = functions.TEA.scaling.CEPCI_scale(base_year=CEPCI_baseline_year,
                                                                                 design_year=CEPCI_year,
                                                                                 value=baseline_CAPEX_2000_currency)

    power_scaled_CAPEX = functions.TEA.power_scale(baseline_size=baseline_size,
                                                   design_size=mass_evaporated_water_per_hour,
                                                   baseline_cost=baseline_CAPEX_updated_year_and_currency,
                                                   scaling_factor=reference_scaling_factor)

    CAPEX_distribution_draws = functions.MonteCarloSimulation.to_fixed_MC_array(power_scaled_CAPEX)

    CAPEX = PresentValue(values=CAPEX_distribution_draws,
                         name="CAPEX Dryer",
                         short_label="CAPEX dry")

    return CAPEX
