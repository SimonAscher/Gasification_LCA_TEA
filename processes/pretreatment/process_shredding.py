import numpy as np

from dataclasses import dataclass
from config import settings
from objects import Process
from objects import Requirements, Electricity, AnnualValue
from processes.pretreatment.utils import electricity_shredding
from functions.TEA.CAPEX_estimation import get_shredding_CAPEX_distribution
from functions.TEA.cost_benefit_components import get_operation_and_maintenance_cost


@dataclass()
class FeedstockBaleShredding(Process):
    name: str = "Feedstock bale shredding"
    short_label: str = "Shred"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, MC_iterations=settings.user_inputs.general.MC_iterations):
        """
        Calculate the requirements for feedstock bale shredding.

        Parameters
        ----------
        MC_iterations: int
             Number of Monte Carlo iterations.
        """

        # Initialise storage list
        electricity_requirement_shredding = []

        # Calculate electricity requirements
        for _, count in enumerate(np.arange(MC_iterations)):
            electricity_requirement_shredding.append(electricity_shredding())

        # Get economic requirements
        CAPEX = get_shredding_CAPEX_distribution()
        o_and_m_costs = get_operation_and_maintenance_cost(CAPEX.values)

        # Initialise Requirements object and add requirements
        feedstock_shredding_requirements = Requirements(name=self.name)
        feedstock_shredding_requirements.add_requirement(
            Electricity(values=electricity_requirement_shredding, name="Electricity use for feedstock bale shredding"))
        feedstock_shredding_requirements.add_requirement(CAPEX)
        feedstock_shredding_requirements.add_requirement(AnnualValue(name="O&M Costs Feedstock Shredder",
                                                                     short_label="O&M Shrd",
                                                                     values=o_and_m_costs,
                                                                     tag="O&M"))

        # Add requirements to object
        self.add_requirements(feedstock_shredding_requirements)
