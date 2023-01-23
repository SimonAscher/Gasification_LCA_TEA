import numpy as np

from functions.general.predictions_to_distributions import get_all_prediction_distributions
from functions.MonteCarloAnalysis import to_MC_array, make_dist
from config import settings
from configs import triangular, gaussian, process_GWP_output, process_GWP_output_MC
from .utils import load_biochar_properties_data


def biochar_soil_GWP_MC(biochar_yield_predictions=None, carbon_fraction="default", stability="default"):
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
    # Get defaults
    if biochar_yield_predictions is None:
        biochar_yield_predictions = get_all_prediction_distributions()["Char yield [g/kg wb]"]

    # Calculate biochar yield in kg/FU
    biochar_yield = (np.array(biochar_yield_predictions) / 1000) * settings.general.FU

    biochar_properties_data = None
    if carbon_fraction == "default" or stability == "default":
        biochar_properties_data = load_biochar_properties_data()

    # Extract user data on feedstock type and name
    feedstock_name = settings.user_inputs.feedstock_name.lower()
    feedstock_type = settings.user_inputs.feedstock_category.lower()
    feedstock_description = feedstock_type + " " + feedstock_name

    # Initialise some variables
    carbon_fraction_else_case = False
    carbon_fraction_min = None
    carbon_fraction_max = None
    carbon_fraction_mean = None
    carbon_fraction_std = None

    # Get Monte Carlo array of carbon fraction in biochar
    if carbon_fraction == "default":
        # Get data
        carbon_fraction_data = biochar_properties_data["Biochar carbon fraction"]

        # Select appropriate data
        if "rice husk" in feedstock_name or "rice straw" in feedstock_name:
            carbon_fraction_mean = carbon_fraction_data["rice husk and rice straw"]["mean"]
            carbon_fraction_std = carbon_fraction_data["rice husk and rice straw"]["std"]

        elif ("nut" in feedstock_name and "pit" in feedstock_name) or (
                "nut" in feedstock_name and "shell" in feedstock_name) or (
                "nut" in feedstock_name and "stone" in feedstock_name):
            carbon_fraction_mean = carbon_fraction_data["nut shells, pits, and stones"]["mean"]
            carbon_fraction_std = carbon_fraction_data["nut shells, pits, and stones"]["std"]

        elif "wood" in feedstock_type:
            carbon_fraction_mean = carbon_fraction_data["wood"]["mean"]
            carbon_fraction_std = carbon_fraction_data["wood"]["std"]

        elif "manure" in feedstock_type:
            carbon_fraction_mean = carbon_fraction_data["animal manure"]["mean"]
            carbon_fraction_std = carbon_fraction_data["animal manure"]["std"]

        elif "herbaceous" in feedstock_type:
            carbon_fraction_mean = carbon_fraction_data["herbaceous biomass"]["mean"]
            carbon_fraction_std = carbon_fraction_data["herbaceous biomass"]["std"]

        elif ("sludge" in feedstock_name and "sewage" in feedstock_description) or (
                "sludge" in feedstock_name and "paper" in feedstock_description):
            carbon_fraction_mean = carbon_fraction_data["biosolids (paper sludge, sewage sludge)"]["mean"]
            carbon_fraction_std = carbon_fraction_data["biosolids (paper sludge, sewage sludge)"]["std"]

        else:
            carbon_fraction_else_case = True
            carbon_fraction_min = carbon_fraction_data.loc["mean"].min()
            carbon_fraction_max = 0.8985  # Ref: https://doi.org/10.1016/j.biortech.2017.06.177

        # Create Monte Carlo array
        if carbon_fraction_else_case:
            carbon_fraction_array = np.random.default_rng().uniform(low=carbon_fraction_min, high=carbon_fraction_max,
                                                                    size=settings.background.iterations_MC)
        else:
            carbon_fraction_array = make_dist(gaussian(mean=carbon_fraction_mean, std=carbon_fraction_std))

    else:  # Fixed value scenario
        carbon_fraction_array = to_MC_array(carbon_fraction)

    # Get Monte Carlo arrays of recalcitrant and labile carbon fractions
    if stability == "default":  # Use default distribution
        # Get data
        recalcitrant_carbon_data = biochar_properties_data["Biochar recalcitrant carbon fraction"]

        recalcitrant_carbon_array = make_dist(
            triangular(lower=recalcitrant_carbon_data.lower,
                       mode=recalcitrant_carbon_data.mode,
                       upper=recalcitrant_carbon_data.upper))

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
    GWP_from_biogenic = list(GWP_labile)

    # Initialise MC output object
    name_process = "Biochar to soil"

    MC_outputs = process_GWP_output_MC(process_name=name_process)

    # Store values in default MC output object
    for count, entry in enumerate(GWP_total):
        GWP_object = process_GWP_output(process_name=name_process, GWP=entry)
        GWP_object.GWP_from_biogenic = GWP_from_biogenic[count]
        GWP_object.add_subprocess(name=name_process, GWP=entry)

        MC_outputs.add_GWP_object(GWP_object)

    MC_outputs.subprocess_abbreviations = ("Char", )  # add abbreviation of subprocess

    return MC_outputs
