from functions.general.predictions_to_distributions import get_all_prediction_distributions
from functions.MC import to_MC_array, make_dist
from config import settings
from configs import triangular, process_GWP_output, process_GWP_output_MC
import numpy as np


def biochar_soil_GWP_MC(biochar_yield_predictions=get_all_prediction_distributions()["Char yield [g/kg wb]"],
                        carbon_fraction="default", stability="default"):
    """
    Calculate the GWP of applying biochar to soil for all Monte Carlo runs.

    Parameters
    ----------
    biochar_yield_predictions: list
        Monte Carlo predictions of biochar yield [g/kg wb].
    carbon_fraction: str or float
        Fraction of carbon in the final biochar product ("default" uses database values).
    stability: str or float
        Fraction of carbon being recalcitrant - i.e. resistant to decomposition ("default" uses database values).
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

    # Initialise MC output object
    name_process = "Biochar to soil"

    MC_outputs = process_GWP_output_MC(process_name=name_process)

    # Store values in default MC output object
    for count, entry in enumerate(GWP_total):
        GWP_object = process_GWP_output(process_name=name_process, GWP=entry)
        GWP_object.GWP_inc_biogenic = GWP_inc_biogenic[count]
        GWP_object.add_subprocess(name=name_process, GWP=entry)

        MC_outputs.add_GWP_object(GWP_object)

    MC_outputs.subprocess_abbreviations = ("Char", )  # add abbreviation of subprocess

    return MC_outputs

    # TODO: Carbon fraction and recalcitrant carbon fractions are functions of feedstock type (C, Ash content), temp,
    #  etc. - ideally the model would be able to incorporate that. Phyllis database could be used to group different
    #  feedstock types and based on those select realistic carbon fractions etc.
