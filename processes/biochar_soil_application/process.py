from functions.MC import to_MC_array, make_dist
from config import settings
from configs import triangular
import numpy as np


def biochar_soil_CO2_eq(biochar_yield_predictions, carbon_fraction="default", stability="default"):
    """
    Calculates the GWP of applying biochar to soil.

    Parameters
    ----------
    biochar_yield_predictions: list
        Monte Carlo list of biochar yield predictions in [g/kg wb].
    carbon_fraction:
        Fixed value of carbon fraction of biochar as decimal or "default".
    stability
        Fixed value of carbon fraction of biochar as decimal or "default".
    Returns
    -------
        GWP values in kg CO2eq. / FU.
    """

    # Calculate biochar yield in kg/FU
    biochar_yield = (np.array(biochar_yield_predictions) / 1000) * settings.general.FU

    # Get Monte Carlo array of carbon fractions in biochar
    if carbon_fraction == "default":
        carbon_fraction_array = make_dist(triangular(lower=settings.data.biochar.carbon_fraction.lower,
                                                     mode=settings.data.biochar.carbon_fraction.mode,
                                                     upper=settings.data.biochar.carbon_fraction.upper))
    else:  # Fixed value scenario
        carbon_fraction_array = to_MC_array(carbon_fraction)

    # Get Monte Carlo arrays of recalcitrant and labile carbon fractions
    if stability == "default":  # Use default distribution
        recalcitrant_carbon_array = make_dist(triangular(lower=settings.data.biochar.recalcitrant_fraction.lower,
                                                         mode=settings.data.biochar.recalcitrant_fraction.mode,
                                                         upper=settings.data.biochar.recalcitrant_fraction.upper))
    else:  # Fixed value scenario
        recalcitrant_carbon_array = to_MC_array(stability)

    # Calculate labile carbon
    labile_carbon_array = 1 - recalcitrant_carbon_array

    # Calculate GWP from recalcitrant and labile carbon in biochar in [kg CO2eq. / FU]
    GWP_recalcitrant = biochar_yield * (settings.data.molar_masses.CO2 / settings.data.molar_masses.C) * \
                       carbon_fraction_array * recalcitrant_carbon_array * -1
    GWP_labile = biochar_yield * (settings.data.molar_masses.CO2 / settings.data.molar_masses.C) * \
                 carbon_fraction_array * labile_carbon_array

    GWP_total = list(GWP_recalcitrant)

    GWP_inc_biogenic = list(GWP_recalcitrant + GWP_labile)

    # TODO: Carbon fraction and recalcitrant carbon fractions are functions of feedstock type (C, Ash content), temp,
    #  etc. - ideally the model would be able to incorporate that. Phyllis database could be used to group different
    #  feedstock types and based on those select realistic carbon fractions etc.

    # Return final calculated GWPs from biochar soil application
    return GWP_total, {"inc. biogenic GWP": GWP_inc_biogenic, "exc. biogenic GWP": GWP_total, "units": "kg CO2eq./FU"}
