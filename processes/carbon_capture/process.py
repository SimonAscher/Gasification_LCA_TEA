import numpy as np

from dataclasses import dataclass
from config import settings
from objects import Process, Requirements, BiogenicGWP, FossilGWP, Electricity, Heat, AnnualValue
from processes.carbon_capture.utils import carbon_capture_VPSA_post_comb, carbon_capture_amine_post_comb
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from processes.syngas_combustion.process import SyngasCombustion
from functions.TEA.CAPEX_estimation import get_carbon_capture_CAPEX_distribution
from functions.TEA import get_present_value
from functions.TEA.cost_benefit_components import (get_operation_and_maintenance_cost,
                                                   carbon_capture_transport_storage_cost_benefit,
                                                   carbon_capture_amine_consumption_cost_benefit)


@dataclass()
class CarbonCapture(Process):
    name: str = "Carbon capture and storage"
    short_label: str = "CCS"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, ML_predictions=None, syngas_combustion_object=None,
                               cc_method=None, MC_iterations=settings.user_inputs.general.MC_iterations):
        """
        Calculate the requirements and impacts of carbon capture and storage (CCS) process.

        Parameters
        ----------
        ML_predictions: dict
            Dictionary of all predicted model outputs as distributions.
        syngas_combustion_object: object
            Syngas combustion sub model outputs.
        cc_method: str
            Specifies carbon capture method. "VPSA post combustion" by default. Alternatively "Amine post comb" or
            "VPSA pre combustion" (not yet supported).
        MC_iterations: int
            Number of Monte Carlo iterations.
        """
        # Get defaults
        if ML_predictions is None:
            ML_predictions = get_all_prediction_distributions()
        if syngas_combustion_object is None:
            syngas_combustion_object = SyngasCombustion()
        if cc_method is None:
            cc_method = "VPSA post combustion"

        # Initialise MC output object
        if cc_method == "VPSA pre combustion":
            name_process = "Carbon capture - VPSA pre comb."
        elif cc_method == "Amine post comb":
            name_process = "Carbon capture - Amine post comb."
        elif cc_method == "VPSA post combustion":  # default option
            name_process = "Carbon capture - VPSA post comb."
        else:
            raise ValueError("Carbon capture method not supported")

        # Initialise Requirements object and add requirements
        CCS_requirements = Requirements(name="Carbon capture an storage")

        # Do analysis for post combustion process' which act on the flue gas

        # Initialise lists for storage
        captured_CO2_fossil = []
        captured_CO2_biogenic = []
        electricity_req = []
        heat_req = []

        # Get emissions from syngas combustion
        # Run a few checks to make sure data from syngas combustion model is of right format.
        if len(syngas_combustion_object.requirements) != 1 \
                or len(syngas_combustion_object.requirements[0].biogenic_GWP) != 1 \
                or len(syngas_combustion_object.requirements[0].fossil_GWP) != 1:
            raise ValueError("Check outputs from syngas combustion model are in right format")

        syngas_combustion_biogenic_CO2 = syngas_combustion_object.requirements[0].biogenic_GWP[0].values
        syngas_combustion_fossil_CO2 = syngas_combustion_object.requirements[0].fossil_GWP[0].values

        if cc_method in ["Amine post comb", "VPSA post combustion"]:
            for _, count in enumerate(np.arange(len(syngas_combustion_fossil_CO2))):
                # Get carbon capture requirements and recovery rate based on selected process
                cc_reqs = None
                if cc_method == "Amine post comb":
                    cc_reqs = carbon_capture_amine_post_comb()
                elif cc_method == "VPSA post combustion":  # default option
                    cc_reqs = carbon_capture_VPSA_post_comb()

                # Calculate captured CO2 [kg CO2eq./FU]
                captured_CO2_fossil.append(-1 * syngas_combustion_fossil_CO2[count] * cc_reqs["Recovery"])
                captured_CO2_biogenic.append(-1 * syngas_combustion_biogenic_CO2[count] * cc_reqs["Recovery"])
                current_captured_CO2_total = captured_CO2_fossil[count] + captured_CO2_biogenic[count]
                # Calculate other requirements
                electricity_req.append(-1 * current_captured_CO2_total * cc_reqs["Electricity consumption"])
                heat_req.append(-1 * current_captured_CO2_total * cc_reqs["Heat consumption"])

            # Add requirements to requirement object
            CCS_requirements.add_requirement(BiogenicGWP
                                             (values=captured_CO2_biogenic, name="Captured biogenic CO2",
                                              short_label="$CO_{2}$ biogenic", negative_emissions=True))
            CCS_requirements.add_requirement(FossilGWP(values=captured_CO2_fossil, name="Captured fossil CO2",
                                                       short_label="$CO_{2}$ fossil"))
            CCS_requirements.add_requirement(Electricity(values=electricity_req,
                                                         name="Electricity use for carbon capture"))
            CCS_requirements.add_requirement(Heat(values=heat_req, name="Heat use for carbon capture"))

        # Do analysis for pre combustion process which acts on the syngas
        elif cc_method == "VPSA pre combustion":
            # Currently not included - would need to include a water gas shift rector to convert CO to CO2
            # (CO + H2O ⇌ CO2 + H2). From here could calculate syngas composition after shifting - apply capture and
            # then compare to conventional process. Look at syngas combustion model to see how to calculate GWP from
            # syngas combustion. Will have similar process here but with most CO2 already extracted.
            raise ValueError(
                "Pre combustion carbon capture currently not supported as other methods deemed more suitable.")

        else:
            raise ValueError("Carbon capture method not supported")

        # Economic requirements
        CO2_capture_rate = list(np.add(captured_CO2_fossil, captured_CO2_biogenic))  # [tonne CO2/FU]
        CAPEX = get_carbon_capture_CAPEX_distribution(CO2_capture_rate)

        o_and_m_costs = get_operation_and_maintenance_cost(get_present_value(values=CAPEX.values,
                                                                             value_type="AV"))

        CC_transport, CC_storage = carbon_capture_transport_storage_cost_benefit(CO2_capture_rate)

        CCS_requirements.add_requirement(CAPEX)
        CCS_requirements.add_requirement(AnnualValue(name="O&M Costs Carbon Capture",
                                                     short_label="O&M CC",
                                                     values=o_and_m_costs,
                                                     tag="O&M"))
        CCS_requirements.add_requirement(CC_transport)
        CCS_requirements.add_requirement(CC_storage)

        if cc_method == "Amine post comb":
            CCS_requirements.add_requirement(carbon_capture_amine_consumption_cost_benefit(CO2_capture_rate))

        # Add requirements to object
        self.add_requirements(CCS_requirements)

        # Store some other useful input data
        self.information = cc_method
