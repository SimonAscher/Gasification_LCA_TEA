import functions

from dataclasses import dataclass
from objects import Process, Requirements, Electricity, Heat, AnnualValue
from functions.general.utility import kJ_to_kWh
from processes.pretreatment.utils import energy_drying
from functions.TEA.CAPEX_estimation import get_dryer_CAPEX_distribution
from functions.TEA.cost_benefit_components import get_operation_and_maintenance_cost


@dataclass()
class FeedstockDrying(Process):
    name: str = "Feedstock drying"
    short_label: str = "Dry"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, energy_drying_dict=None):
        """
        Calculate the requirements for feedstock drying.

        Parameters
        ----------
        energy_drying_dict: dict
            Output from energy_drying function containing heat and electricity requirements and units and heat source.

        """
        # Get defaults
        if energy_drying_dict is None:
            energy_drying_dict = energy_drying()

        # Convert units to kWh if not given in kWh already
        if energy_drying_dict["units"] == "kJ":
            energy_drying_dict["heat"] = kJ_to_kWh(energy_drying_dict["heat"])  # [kWh/FU]
            energy_drying_dict["electricity"] = kJ_to_kWh(energy_drying_dict["electricity"])  # [kWh/FU]
            energy_drying_dict["units"] = "kWh"

        # Get economic requirements
        CAPEX = get_dryer_CAPEX_distribution()
        o_and_m_costs = get_operation_and_maintenance_cost(CAPEX.values)

        # Initialise Requirements object and add requirements
        feedstock_drying_requirements = Requirements(name=self.name)
        feedstock_drying_requirements.add_requirement(
            Heat(values=list(functions.MonteCarloSimulation.to_fixed_MC_array(energy_drying_dict["heat"])),
                 name="Heat use for feedstock drying",
                 source=energy_drying_dict["heat source"]))
        feedstock_drying_requirements.add_requirement(
            Electricity(values=list(functions.MonteCarloSimulation.to_fixed_MC_array(energy_drying_dict
                                                                                     ["electricity"])),
                        name="Electricity use for feedstock drying"))
        feedstock_drying_requirements.add_requirement(CAPEX)
        feedstock_drying_requirements.add_requirement(AnnualValue(name="O&M Costs Feedstock Dryer",
                                                                  short_label="O&M Dry",
                                                                  values=o_and_m_costs,
                                                                  tag="O&M"))

        # Add requirements to object
        self.add_requirements(feedstock_drying_requirements)
