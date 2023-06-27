import numpy as np

from dataclasses import dataclass
from config import settings
from functions.LCA import get_CO2_equ
from objects import triangular_dist_maker, gaussian_dist_maker
from objects import Process
from objects import Requirements, BiogenicGWP, FossilGWP
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from functions.MonteCarloSimulation import to_fixed_MC_array, get_distribution_draws
from processes.biochar_soil_application.utils import load_biochar_properties_data, avoided_N2O_emissions


@dataclass()
class BiocharSoilApplication(Process):
    name: str = "Biochar soil application"
    short_label: str = "BC"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, biochar_yield_predictions=None, carbon_fraction=None, stability=None):
        """
        Gets the requirements and impacts of applying biochar to soil.

        Parameters
        ----------
        biochar_yield_predictions: list
            Monte Carlo predictions of biochar yield [g/kg wb].
        carbon_fraction: None or float
            Fraction of carbon in the final biochar product ("None" uses database values).
        stability: None or float
            Fraction of carbon being recalcitrant - i.e. resistant to decomposition ("None" uses database values).
        """
        # Get defaults
        if biochar_yield_predictions is None:
            biochar_yield_predictions = get_all_prediction_distributions()["Char yield [g/kg wb]"]

        biochar_properties_data = None
        if carbon_fraction is None or stability is None:
            biochar_properties_data = load_biochar_properties_data()

        # Calculate biochar yield
        biochar_yield = (np.array(biochar_yield_predictions) / 1000) * settings.general.FU  # [kg/FU]

        # Extract user data on feedstock type and name
        feedstock_name = settings.user_inputs.feedstock.name.lower()
        feedstock_type = settings.user_inputs.feedstock.category.lower()
        feedstock_description = feedstock_type + " " + feedstock_name

        # Initialise variables used to fetch correct carbon fraction in biochar
        carbon_fraction_else_case = False
        carbon_fraction_min = None
        carbon_fraction_max = None
        carbon_fraction_mean = None
        carbon_fraction_std = None

        # Get Monte Carlo array of carbon fraction in biochar
        if carbon_fraction is None:
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
                # TODO: Find data on plastic and municipal solid waste biochar carbon content if possible.

            # Create Monte Carlo array
            if carbon_fraction_else_case:
                carbon_fraction_array = np.random.default_rng().uniform(low=carbon_fraction_min,
                                                                        high=carbon_fraction_max,
                                                                        size=settings.user_inputs.general.MC_iterations)
            else:
                carbon_fraction_array = get_distribution_draws(
                    gaussian_dist_maker(mean=carbon_fraction_mean, std=carbon_fraction_std))

        else:  # Fixed value scenario
            carbon_fraction_array = to_fixed_MC_array(carbon_fraction)

        # Get Monte Carlo arrays of recalcitrant and labile carbon fractions
        if stability is None:  # Use default distribution
            # Get data
            recalcitrant_carbon_data = biochar_properties_data["Biochar recalcitrant carbon fraction"]

            recalcitrant_carbon_array = get_distribution_draws(triangular_dist_maker(lower=recalcitrant_carbon_data.lower,
                                                                                     mode=recalcitrant_carbon_data.mode,
                                                                                     upper=recalcitrant_carbon_data.upper))

        else:  # Fixed value scenario
            recalcitrant_carbon_array = to_fixed_MC_array(stability)

        # Calculate labile carbon
        labile_carbon_array = 1 - recalcitrant_carbon_array

        # Calculate GWP from recalcitrant and labile carbon in biochar in [kg CO2eq. / FU]
        GWP_recalcitrant = biochar_yield * (settings.data.molar_masses.CO2 / settings.data.molar_masses.C) * \
                           carbon_fraction_array * recalcitrant_carbon_array * -1  # [kg CO2eq. / FU]
        GWP_labile = biochar_yield * (settings.data.molar_masses.CO2 / settings.data.molar_masses.C) * \
                     carbon_fraction_array * labile_carbon_array  # [kg CO2eq. / FU]

        # Get background data on biogenic nature of feedstock
        try:
            biogenic_fraction = settings.data.biogenic_fractions[settings.user_inputs.feedstock.category]
        except:  # BoxKeyError
            biogenic_fraction = 1
            raise Warning("No default biogenic fraction available for this feedstock type - 100% biogenic assumed.")

        # Calculate biogenic and fossil emissions due to carbon in biochar
        recalcitrant_biogenic_CO2 = list(GWP_recalcitrant * biogenic_fraction)
        recalcitrant_fossil_CO2 = list(GWP_recalcitrant * (1-biogenic_fraction))
        labile_biogenic_CO2 = list(GWP_labile * biogenic_fraction)
        labile_fossil_CO2 = list(GWP_labile * (1 - biogenic_fraction))

        # Calculate benefits due to reduced N2O emissions from soil due to biochar application
        avoided_N20 = list(map(avoided_N2O_emissions, biochar_yield))  # N20/FU
        avoided_N2O_GWP = [get_CO2_equ(N2O=i) for i in avoided_N20]  # kg CO2 eq./FU

        # Requirements related to biochar to soil application

        # Initialise Requirements object and add requirements
        biochar_requirements = Requirements(name="Biochar soil application")

        if biogenic_fraction > 0:
            biochar_requirements.add_requirement(
                BiogenicGWP(values=list(labile_biogenic_CO2),
                            name="Emissions due to labile biogenic fraction of biochar",
                            short_label="Labile $C_{b}$"))
            biochar_requirements.add_requirement(
                BiogenicGWP(values=list(recalcitrant_biogenic_CO2),
                            name="Avoided emissions due to recalcitrant biogenic fraction of biochar",
                            negative_emissions=True,
                            short_label="Recalc. $C_{b}$"))
        if biogenic_fraction < 1:
            biochar_requirements.add_requirement(
                FossilGWP(values=list(labile_fossil_CO2),
                          name="Emissions due to labile non-biogenic fraction of biochar",
                          short_label="Labile $C_{f}$"))
            biochar_requirements.add_requirement(
                FossilGWP(values=list(recalcitrant_fossil_CO2),
                          name="Avoided emissions due to recalcitrant non-biogenic fraction of biochar",
                          negative_emissions=True,
                          short_label="Recalc. $C_{f}$"))

        # Avoided emissions due to lowered N2O emissions from soil after biochar application
        biochar_requirements.add_requirement(
            BiogenicGWP(values=avoided_N2O_GWP,
                        name="Avoided emissions due to lowered N2O emissions from soil",
                        negative_emissions=True,
                        short_label="Avoid. $N_{2}O$"))

        # Add requirements to object
        self.add_requirements(biochar_requirements)
