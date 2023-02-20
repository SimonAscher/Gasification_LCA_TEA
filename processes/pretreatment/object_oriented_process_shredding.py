import numpy as np

from dataclasses import dataclass
from config import settings
from configs.process_objects import Process
from configs.requirement_objects import Requirements, Electricity
from processes.pretreatment.utils import electricity_shredding


@dataclass()
class FeedstockBaleShredding(Process):
    name: str = "Feedstock bale shredding"
    short_label: str = "Shred"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, MC_iterations=settings.background.iterations_MC):
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

        # Initialise Requirements object and add requirements
        feedstock_shredding_requirements = Requirements(name=self.name)
        feedstock_shredding_requirements.add_requirement(
            Electricity(values=electricity_requirement_shredding, name="Electricity use for feedstock bale shredding"))

        # Add requirements to object
        self.add_requirements(feedstock_shredding_requirements)
