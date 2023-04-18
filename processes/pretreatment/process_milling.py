import numpy as np
import warnings

from dataclasses import dataclass
from config import settings
from objects import Process
from objects import Requirements, Electricity
from processes.pretreatment.utils import electricity_milling
from dynaconf.loaders.toml_loader import write


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

        # Initialise Requirements object and add requirements
        feedstock_drying_requirements = Requirements(name=self.name)
        feedstock_drying_requirements.add_requirement(Electricity(values=electricity_req,
                                                                  name="Electricity use for feedstock milling"))

        # Add requirements to object
        self.add_requirements(feedstock_drying_requirements)
