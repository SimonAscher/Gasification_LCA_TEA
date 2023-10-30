import math

import numpy as np

from dataclasses import dataclass
from config import settings
from objects import Process, Requirements, Electricity, fixed_dist_maker, AnnualValue
from processes.pretreatment.utils import electricity_pelleting
from dynaconf.loaders.toml_loader import write
from functions.TEA.CAPEX_estimation import get_pellet_mill_and_cooler_CAPEX_distribution
from functions.TEA.cost_benefit_components import get_operation_and_maintenance_cost


@dataclass()
class FeedstockPelleting(Process):
    name: str = "Feedstock Pelleting"
    short_label: str = "Pel"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, particle_size=None, MC_iterations=settings.user_inputs.general.MC_iterations):
        """
        Calculate the requirements for feedstock pelleting.
        Note: Ensure that milling function is run first to update particle size post milling.

        Parameters
        ----------
        particle_size: float
            Defines the particle size in mm. Uses post milling particle size if applicable.

        MC_iterations: int
            Number of Monte Carlo iterations.
        """

        # Get defaults
        if particle_size is None:
            try:
                particle_size = settings.user_inputs.feedstock.particle_size_post_milling
            except:
                particle_size = settings.user_inputs.feedstock.particle_size_ar

        # Initialise storage list
        electricity_requirement_pelleting = []

        # Get electricity requirements for pelleting
        for _, count in enumerate(np.arange(MC_iterations)):
            electricity_requirement_pelleting.append(electricity_pelleting(particle_size=particle_size))

        # Update toml document with average particle size after milling
        particle_size_post_pelleting_mm = 6.35  # [mm] source: "10.13031/aea.30.9719"
        user_inputs_file_path = settings.settings_module[-2]
        write(user_inputs_file_path,
              {"default":
                   {"user_inputs":
                        {"feedstock":
                             {"particle_size_post_pelleting": float(particle_size_post_pelleting_mm)}}}},
              merge=True)

        # Get economic requirements
        CAPEX_mill, CAPEX_cooler = get_pellet_mill_and_cooler_CAPEX_distribution()

        # Check if CAPEX occurs more than once
        global_life_span = settings.user_inputs.general.system_life_span
        if CAPEX_mill.number_of_periods < global_life_span:
            repetitions_mill = math.floor(global_life_span / CAPEX_mill.number_of_periods)
            CAPEX_mill.values = list(np.multiply(CAPEX_mill.values, repetitions_mill))
        if CAPEX_cooler.number_of_periods < global_life_span:
            repetitions_cooler = math.floor(global_life_span / CAPEX_mill.number_of_periods)
            CAPEX_cooler.values = list(np.multiply(CAPEX_cooler.values, repetitions_cooler))

        # Calculate O&M Cost
        o_and_m_mill = get_operation_and_maintenance_cost(CAPEX_mill.values, fixed_dist_maker(0.10))
        o_and_m_cooler = get_operation_and_maintenance_cost(CAPEX_cooler.values, fixed_dist_maker(0.10))
        # O&M cost = 10%
        # Source: "Development of agri-pellet production cost and optimum size, Sultana et al., 2010 and Economics of
        # producing fuel pellets from biomass", Mani et al., 2006"

        # Initialise Requirements object and add requirements
        feedstock_pelleting_requirements = Requirements(name=self.name)
        feedstock_pelleting_requirements.add_requirement(Electricity(values=electricity_requirement_pelleting,
                                                                     name="Electricity use for feedstock pelleting"))
        feedstock_pelleting_requirements.add_requirement(CAPEX_mill)
        feedstock_pelleting_requirements.add_requirement(CAPEX_cooler)
        feedstock_pelleting_requirements.add_requirement(AnnualValue(name="O&M Costs Pellet Mill",
                                                                     short_label="O&M Pellet-M",
                                                                     values=o_and_m_mill,
                                                                     tag="O&M"))
        feedstock_pelleting_requirements.add_requirement(AnnualValue(name="O&M Costs Pellet Cooler",
                                                                     short_label="O&M Pellet-C",
                                                                     values=o_and_m_cooler,
                                                                     tag="O&M"))

        # Add requirements to object
        self.add_requirements(feedstock_pelleting_requirements)
