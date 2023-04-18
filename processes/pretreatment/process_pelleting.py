import numpy as np

from dataclasses import dataclass
from config import settings
from objects import Process
from objects import Requirements, Electricity
from processes.pretreatment.utils import electricity_pelleting
from dynaconf.loaders.toml_loader import write


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

        # Initialise Requirements object and add requirements
        feedstock_pelleting_requirements = Requirements(name=self.name)
        feedstock_pelleting_requirements.add_requirement(Electricity(values=electricity_requirement_pelleting,
                                                                     name="Electricity use for feedstock pelleting"))

        # Add requirements to object
        self.add_requirements(feedstock_pelleting_requirements)
