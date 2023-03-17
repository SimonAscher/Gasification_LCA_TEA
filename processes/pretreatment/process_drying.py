from dataclasses import dataclass
from configs.process_objects import Process
from configs.requirement_objects import Requirements, Electricity, Heat
from functions.general.utility import kJ_to_kWh
from processes.pretreatment.utils import energy_drying
from functions.MonteCarloSimulation import to_fixed_MC_array


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

        # Initialise Requirements object and add requirements
        feedstock_drying_requirements = Requirements(name=self.name)
        feedstock_drying_requirements.add_requirement(Heat(values=list(to_fixed_MC_array(energy_drying_dict["heat"])),
                                                           name="Feedstock drying heat requirement",
                                                           source=energy_drying_dict["heat source"]))
        feedstock_drying_requirements.add_requirement(Electricity(values=list(to_fixed_MC_array(energy_drying_dict
                                                                                                ["electricity"])),
                                                                  name="Feedstock drying electricity requirement"))

        # Add requirements to object
        self.add_requirements(feedstock_drying_requirements)
