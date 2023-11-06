from config import settings
from objects import Process
from objects import Requirements, Electricity, Heat, Oxygen, Steam, AnnualValue
from dataclasses import dataclass
from processes.gasification.utils import mass_agent, demands_ele_aux_gas_cleaning, demands_heat_auxiliary_gasification
from functions.MonteCarloSimulation import to_fixed_MC_array
from processes.CHP import CombinedHeatPower
from functions.TEA.CAPEX_estimation import (get_gasification_and_gas_cleaning_CAPEX_distributions,
                                            get_boiler_CAPEX_distribution)
from functions.TEA.cost_benefit_components import get_operation_and_maintenance_cost, oxygen_consumption_cost_benefit


@dataclass()
class Gasification(Process):
    name: str = "Gasification"
    short_label: str = "G"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, agent_type=None, agent_mass=None, FU=None, MC_iterations=None):
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
            agent_type = settings.user_inputs.process_conditions.gasifying_agent

        if agent_mass is None:
            agent_mass = mass_agent(agent_type=agent_type)

        if FU is None:
            FU = settings.general["FU"]

        if MC_iterations is None:
            MC_iterations = settings.user_inputs.general.MC_iterations

        # Requirements related to agent provision
        agent_requirements = Requirements(name="Agent")  # Initialise Requirements object

        # Model emissions and energy requirements based on agent type
        if agent_type == "Air" or agent_type == "Other":
            # Note: Currently agent_type = "Other" treated as air.
            # Note: Currently no direct requirements due to air as agent
            pass

        elif agent_type == "Oxygen":
            total_oxygen_mass = agent_mass["Oxygen"] * FU  # [kg O2/FU]
            agent_requirements.add_requirement(Oxygen(name="Electricity for oxygen production",
                                                      short_label="Ele",
                                                      values=list(to_fixed_MC_array(total_oxygen_mass))))

            # Get economic requirement for oxygen provision
            Cost_O2 = oxygen_consumption_cost_benefit(unit_oxygen_requirement=agent_mass["Oxygen"])
            agent_requirements.add_requirement(Cost_O2)

        elif agent_type == "Steam" or agent_type == "Air + steam":
            # Get heat requirement for steam production
            total_steam_mass = agent_mass["Steam"] * FU  # [kg Steam/FU]
            agent_requirements.add_requirement(Steam(short_label="Heat",
                                                     name="Heat for steam production",
                                                     values=list(to_fixed_MC_array(total_steam_mass))))

            # Get economic requirement for boiler to generate steam
            CAPEX_boiler = get_boiler_CAPEX_distribution(unit_steam_requirement=agent_mass["Steam"])
            o_and_m_costs_boiler = get_operation_and_maintenance_cost(CAPEX_boiler.values)
            agent_requirements.add_requirement(CAPEX_boiler)
            agent_requirements.add_requirement(AnnualValue(name="O&M Costs Boiler for Steam Generation",
                                                           short_label="O&M Stm",
                                                           values=o_and_m_costs_boiler,
                                                           tag="O&M"))

        else:
            raise ValueError("Wrong agent type given")

        # Requirements related to auxiliary demands
        auxiliary_requirements = Requirements(name="Auxiliary")  # Initialise Requirements object

        # Electricity
        electricity_auxiliary = []
        for _ in range(MC_iterations):
            electricity_auxiliary.append(demands_ele_aux_gas_cleaning())

        # Heat
        heat_auxiliary = demands_heat_auxiliary_gasification(CHP_results_object=CombinedHeatPower(),
                                                             MC_iterations=MC_iterations)

        auxiliary_requirements.add_requirement(Electricity(values=electricity_auxiliary,
                                                           name="Electricity for auxiliary demands and gas cleaning"))
        auxiliary_requirements.add_requirement(Heat(values=heat_auxiliary,
                                                    name="Heat for auxiliary demands and gas cleaning"))

        # Economic requirements
        economic_requirements = Requirements(name="Economic")  # Initialise Requirements object

        CAPEX_results = get_gasification_and_gas_cleaning_CAPEX_distributions()
        CAPEX_gasification, CAPEX_gas_cleaning = CAPEX_results
        o_and_m_costs_gasification = get_operation_and_maintenance_cost(CAPEX_gasification.values)
        o_and_m_costs_gas_cleaning = get_operation_and_maintenance_cost(CAPEX_gas_cleaning.values)

        economic_requirements.add_requirement(CAPEX_gasification)
        economic_requirements.add_requirement(CAPEX_gas_cleaning)
        economic_requirements.add_requirement(AnnualValue(name="O&M Costs Gasifier",
                                                          short_label="O&M Gas.",
                                                          values=o_and_m_costs_gasification,
                                                          tag="O&M"))
        economic_requirements.add_requirement(AnnualValue(name="O&M Costs Gas Cleaning",
                                                          short_label="O&M Gas Clean.",
                                                          values=o_and_m_costs_gas_cleaning,
                                                          tag="O&M"))

        # Add requirements to object
        self.add_requirements(agent_requirements)
        self.add_requirements(auxiliary_requirements)
        self.add_requirements(economic_requirements)
