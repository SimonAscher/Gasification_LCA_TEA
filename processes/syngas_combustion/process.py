import numpy as np

from dataclasses import dataclass
from config import settings
from objects import Process
from objects import Requirements, BiogenicGWP, FossilGWP
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from functions.general.utility import scale_gas_fractions
from processes.syngas_combustion.utils import syngas_combustion_CO2_eq


@dataclass()
class SyngasCombustion(Process):
    name: str = "Syngas combustion"
    short_label: str = "Syn"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, ML_predictions=None):
        """
        Calculate the requirements and impacts of syngas combustion.

        Parameters
        ----------
        ML_predictions: dict
            Dictionary of all predicted model outputs as distributions.
        """

        # Get defaults
        if ML_predictions is None:
            ML_predictions = get_all_prediction_distributions()

        # Extract gas yield ML predictions for later use
        gas_yields = ML_predictions["Gas yield [Nm3/kg wb]"]

        # Create dictionary of gas species only
        gas_fractions = ML_predictions.copy()

        # Drop unrequired variables if they exist in dictionary:
        if "LHV [MJ/Nm3]" in gas_fractions:
            gas_fractions.pop("LHV [MJ/Nm3]")
        if "Gas yield [Nm3/kg wb]" in gas_fractions:
            gas_fractions.pop("Gas yield [Nm3/kg wb]")
        if "Tar [g/Nm3]" in gas_fractions:
            gas_fractions.pop("Tar [g/Nm3]")
        if "Char yield [g/kg wb]" in gas_fractions:
            gas_fractions.pop("Char yield [g/kg wb]")

        # Scale gas fractions, so that they all sum up to 1. Turn from percentages to decimals.
        scaled_gas_fractions = scale_gas_fractions(gas_fractions, gas_fractions_format="percentages")

        # Calculate CO2 emission from combustion
        total_CO2 = syngas_combustion_CO2_eq(scaled_gas_fractions, gas_yields)  # [kg CO2eq./FU]

        # Get background data on the feedstock
        try:
            biogenic_fraction = settings.data.biogenic_fractions[settings.user_inputs.feedstock.category]
        except:  # BoxKeyError
            raise Warning("No default biogenic fraction available for this feedstock type - 0% biogenic assumed.")
            biogenic_fraction = 0

        # Calculate biogenic and fossil emissions
        biogenic_CO2 = list(np.array(total_CO2) * biogenic_fraction)
        fossil_CO2 = list(np.array(total_CO2) * (1 - biogenic_fraction))

        # Initialise Requirements object and add requirements
        syngas_combustion_requirements = Requirements(name="Syngas combustion")
        syngas_combustion_requirements.add_requirement(BiogenicGWP(values=biogenic_CO2,
                                                                   name="Biogenic CO2 emission from syngas combustion",
                                                                   short_label="Syn. comb."))
        syngas_combustion_requirements.add_requirement(FossilGWP(values=fossil_CO2,
                                                                 name="Fossil CO2 emissions from syngas combustion",
                                                                 short_label="Syn. comb."))

        # Add requirements to object
        self.add_requirements(syngas_combustion_requirements)
