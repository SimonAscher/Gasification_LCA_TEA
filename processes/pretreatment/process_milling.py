import math
import warnings

import numpy as np

from dataclasses import dataclass
from config import settings
from objects import Process, Requirements, Electricity, range_dist_maker, AnnualValue
from processes.pretreatment.utils import electricity_milling
from dynaconf.loaders.toml_loader import write
from functions.TEA.cost_benefit_components import get_operation_and_maintenance_cost
from functions.TEA.CAPEX_estimation import get_milling_CAPEX_distribution


@dataclass()
class FeedstockMilling(Process):
    name: str = "Feedstock Milling"
    short_label: str = "Mill"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, screensize=3.2, MC_iterations=settings.user_inputs.general.MC_iterations):
        """
        Calculate the requirements for feedstock milling.

        Parameters
        ----------
        screensize: float
            Defines which screensize should be used for the mill [mm].

        MC_iterations: int
            Number of Monte Carlo iterations.
        """
        # Initialise list to store electricity requirements and particle sizes
        electricity_req = []
        particle_sizes = []

        # Calculate electricity requirements and particle sizes
        for _, count in enumerate(np.arange(MC_iterations)):
            electricity_instance, particle_size_instance = electricity_milling(screensize=screensize)
            electricity_req.append(electricity_instance)
            particle_sizes.append(particle_size_instance)

        # Update toml document with average particle size after milling
        average_particle_size = np.mean(particle_sizes)
        if float(average_particle_size) > settings.user_inputs.feedstock.particle_size_ar:
            warnings.warn("Milling likely obsolete as particle size already very fine.")
        else:
            user_inputs_file_path = settings.settings_module[-2]
            write(user_inputs_file_path,
                  {"default":
                       {"user_inputs":
                            {"feedstock":
                                 {"particle_size_post_milling": float(average_particle_size)}}}},
                  merge=True)

        # Get economic requirements
        CAPEX = get_milling_CAPEX_distribution()

        # Check if CAPEX occurs more than once
        global_life_span = settings.user_inputs.general.system_life_span
        if CAPEX.number_of_periods < global_life_span:
            repetitions = math.floor(global_life_span / CAPEX.number_of_periods)
            CAPEX.values = list(np.multiply(CAPEX.values, repetitions))

        # Calculate O&M Cost
        o_and_m_costs = get_operation_and_maintenance_cost(CAPEX.values, range_dist_maker(0.10, 0.18))
        # operation_and_maintenance_cost = 10% to 18%
        # Sources: "Development of agri-pellet production cost and optimum size", Sultana et al., 2010
        # "Economics of producing fuel pellets from biomass", Mani et al., 2006

        # Initialise Requirements object and add requirements
        feedstock_milling_requirements = Requirements(name=self.name)
        feedstock_milling_requirements.add_requirement(Electricity(values=electricity_req,
                                                                   name="Electricity use for feedstock milling"))
        feedstock_milling_requirements.add_requirement(CAPEX)
        feedstock_milling_requirements.add_requirement(AnnualValue(name="O&M Costs Feedstock Mill",
                                                                   short_label="O&M Mill",
                                                                   values=o_and_m_costs,
                                                                   tag="O&M"))

        # Add requirements to object
        self.add_requirements(feedstock_milling_requirements)
