import numpy as np
import warnings

from dataclasses import dataclass
from config import settings
from configs.process_objects import Process
from configs.requirement_objects import Requirements, Electricity
from processes.pretreatment.utils import electricity_milling
from functions.general.utility.toml_handling import update_user_inputs_toml


@dataclass()
class FeedstockMilling(Process):
    name: str = "Feedstock Milling"
    short_label: str = "Mill"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, screensize=3.2, MC_iterations=settings.background.iterations_MC):
        """
        Calculate the requirements for feedstock milling.

        Parameters
        ----------
        screensize: float
            Defines which screensize should be used for the mill.

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
        if average_particle_size > settings.user_inputs["particle size"]:
            warnings.warn("Milling likely obsolete as particle size already very fine.")
        else:
            update_user_inputs_toml("particle size after milling", float(average_particle_size))

        # Initialise Requirements object and add requirements
        feedstock_drying_requirements = Requirements(name=self.name)
        feedstock_drying_requirements.add_requirement(Electricity(values=electricity_req,
                                                                  name="Electricity use for feedstock milling"))

        # Add requirements to object
        self.add_requirements(feedstock_drying_requirements)
