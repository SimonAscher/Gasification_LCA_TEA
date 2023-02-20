import numpy as np

from dataclasses import dataclass
from config import settings
from configs.process_objects import Process
from configs.requirement_objects import Requirements, Electricity
from functions.general.utility.toml_handling import update_user_inputs_toml
from processes.pretreatment.utils import electricity_pelleting


@dataclass()
class FeedstockPelleting(Process):
    name: str = "Feedstock Pelleting"
    short_label: str = "Pel"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, particle_size=None, MC_iterations=settings.background.iterations_MC):
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
                particle_size = settings.user_inputs["particle size after milling"]
            except:
                particle_size = settings.user_inputs["particle size"]

        # Initialise storage list
        electricity_requirement_pelleting = []

        # Get electricity requirements for pelleting
        for _, count in enumerate(np.arange(MC_iterations)):
            electricity_requirement_pelleting.append(electricity_pelleting(particle_size=particle_size))

        # Update toml document with average particle size after milling
        particle_size_post_pelleting_mm = 6.35  # [mm] source: "10.13031/aea.30.9719"
        update_user_inputs_toml("particle size after pelleting", float(particle_size_post_pelleting_mm))

        # Initialise Requirements object and add requirements
        feedstock_pelleting_requirements = Requirements(name=self.name)
        feedstock_pelleting_requirements.add_requirement(Electricity(values=electricity_requirement_pelleting,
                                                                     name="Electricity use for feedstock pelleting"))

        # Add requirements to object
        self.add_requirements(feedstock_pelleting_requirements)
