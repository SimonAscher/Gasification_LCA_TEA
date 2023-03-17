from config import settings
from configs.process_objects import Process
from configs.requirement_objects import Requirements, Electricity, Heat, Oxygen, Steam
from dataclasses import dataclass
from processes.gasification.utils import mass_agent, demands_ele_aux_gas_cleaning, demands_heat_auxiliary_gasification
from functions.MonteCarloSimulation import to_fixed_MC_array
from processes.CHP import CombinedHeatPower


@dataclass()
class Gasification(Process):
    name: str = "Gasification"
    short_label: str = "G"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, agent_type=None, agent_mass=None, FU=settings.general["FU"],
                               MC_iterations=settings.background.iterations_MC):
        """
        Calculates all requirements for the gasification process.

        Parameters
        ----------
        agent_type: str
            String specifying which gasifying agent is used.
        agent_mass: dict
            Dictionary with the required mass of agents and their units.
        FU: int
            Functional unit of process in kg.
        MC_iterations: int
            Number of Monte Carlo iterations.
        """

        # Define defaults
        if agent_type is None:
            agent_type = settings.user_inputs["gasifying agent"]

        if agent_mass is None:
            agent_mass = mass_agent(agent_type=agent_type)

        # Requirements related to agent provision

        # Initialise Requirements object
        agent_requirements = Requirements(name="Agent")

        # Model emissions and energy requirements based on agent type
        if agent_type == "Air" or agent_type == "Other":
            # Note: Currently agent_type = "Other" treated as air.
            # Note: Currently no direct requirements due to air as agent
            pass
        elif agent_type == "Air + steam":
            pass

        elif agent_type == "Oxygen":
            total_oxygen_mass = agent_mass["Oxygen"] * FU  # [kg O2/FU]
            agent_requirements.add_requirement(Oxygen(values=list(to_fixed_MC_array(total_oxygen_mass)),
                                                      name="Electricity for oxygen production"))

        elif agent_type == "Steam":
            # Get heat requirement for steam production
            total_steam_mass = agent_mass["Steam"] * FU  # [kg Steam/FU]
            agent_requirements.add_requirement(Steam(values=list(to_fixed_MC_array(total_steam_mass)),
                                                     name="Heat for steam production"))

        else:
            raise ValueError("Wrong agent type given")

        # Requirements related to auxiliary demands

        # Initialise Requirements object and add requirements
        auxiliary_requirements = Requirements(name="Auxiliary")

        # Electricity
        electricity_auxiliary = []
        for _ in range(MC_iterations):
            electricity_auxiliary.append(demands_ele_aux_gas_cleaning())
        auxiliary_requirements.add_requirement(Electricity(values=electricity_auxiliary,
                                                           name="Electricity for auxiliary demands and gas cleaning"))

        # Heat
        heat_auxiliary = demands_heat_auxiliary_gasification(CHP_results_object=CombinedHeatPower(),
                                                             MC_iterations=MC_iterations)

        auxiliary_requirements.add_requirement(Heat(values=heat_auxiliary,
                                                    name="Heat for auxiliary demands and gas cleaning"))

        # Add requirements to object
        self.add_requirements(agent_requirements)
        self.add_requirements(auxiliary_requirements)
