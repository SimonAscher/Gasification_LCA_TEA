import numpy as np

from dataclasses import dataclass
from config import settings
from objects import Process, Requirements, Heat, Electricity, AnnualValue
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from functions.general.utility.unit_conversions import MJ_to_kWh
from functions.TEA.CAPEX_estimation import get_CHP_CAPEX_distribution
from functions.TEA.cost_benefit_components import get_operation_and_maintenance_cost


@dataclass()
class CombinedHeatPower(Process):
    name: str = "Combined heat and power"
    short_label: str = "CHP"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, gas_supplied=None,
                               LHV_gas=None,
                               displaced_heat_source=None,
                               CHP_type=None,
                               efficiency_electrical=None,
                               efficiency_heat=None,
                               demand_parasitic=None,
                               FU=settings.general["FU"]):
        """
        Calculates all requirements and impacts of using syngas for combined heat and power (CHP).

        Parameters
        ----------
        gas_supplied: list
            Monte Carlo Syngas predictions from ML model [Nm3/kg wb].
        LHV_gas: list
            Monte Carlo Syngas LHV predictions from ML model [MJ/Nm3].
        displaced_heat_source: str
            Defines the source of the heat that is to be replaced.
        CHP_type: str
            Defines which type of reference CHP unit is to be used.
        efficiency_electrical: float
            Electrical conversion efficiency as a decimal.
        efficiency_heat: float
            Thermal energy conversion efficiency as a decimal.
        demand_parasitic: float
            Parasitic electricity requirements as a decimal.
        FU: int
            Functional Unit.
        """

        # Get defaults
        if gas_supplied is None or LHV_gas is None:
            all_predictions = get_all_prediction_distributions()
            if gas_supplied is None:
                gas_supplied = all_predictions["Gas yield [Nm3/kg wb]"],
            if LHV_gas is None:
                LHV_gas = all_predictions['LHV [MJ/Nm3]']

        if displaced_heat_source is None:
            displaced_heat_source = "natural gas"

        # Select correct CHP unit data
        if CHP_type is None:
            CHP_type = settings.user_inputs.processes.CHP.type

            if CHP_type == "Jenbacher Type 6 gas engine (1600 kW) (default)":
                efficiency_electrical = settings.data.conversion_efficiencies.CHP.jenbacher_type_6["electrical"]
                efficiency_heat = settings.data.conversion_efficiencies.CHP.jenbacher_type_6["heat"]
                demand_parasitic = settings.data.conversion_efficiencies.CHP.jenbacher_type_6["parasitic"]
            elif CHP_type == "Solid oxide fuel cell (SOFC) (1.7 kW)":
                efficiency_electrical = settings.data.conversion_efficiencies.CHP.SOFC["electrical"]
                efficiency_heat = settings.data.conversion_efficiencies.CHP.SOFC["heat"]
                demand_parasitic = settings.data.conversion_efficiencies.CHP.SOFC["parasitic"]
            elif CHP_type == "Stirling engine (1.2 kW)":
                efficiency_electrical = settings.data.conversion_efficiencies.CHP.stirling_engine["electrical"]
                efficiency_heat = settings.data.conversion_efficiencies.CHP.stirling_engine["heat"]
                demand_parasitic = settings.data.conversion_efficiencies.CHP.stirling_engine["parasitic"]
            elif CHP_type == "Micro gas turbine (30kW)":
                efficiency_electrical = settings.data.conversion_efficiencies.CHP.micro_gas_turbine["electrical"]
                efficiency_heat = settings.data.conversion_efficiencies.CHP.micro_gas_turbine["heat"]
                demand_parasitic = settings.data.conversion_efficiencies.CHP.micro_gas_turbine["parasitic"]
            elif CHP_type == "User defined":
                efficiency_electrical = settings.user_inputs.processes.CHP.electrical_efficiency
                efficiency_heat = settings.user_inputs.processes.CHP.thermal_efficiency
                demand_parasitic = settings.user_inputs.processes.CHP.parasitic_demand
            else:
                raise ValueError("Invalid CHP type specified.")

        # Calculate amount of energy produced
        energy_production_rate = np.array(gas_supplied) * np.array(LHV_gas)  # [MJ/kg]
        energy_produced = MJ_to_kWh(energy_production_rate * FU)  # [kWh/FU]

        # Calculate electricity displacement
        electricity_produced = list((energy_produced * efficiency_electrical) * (1 - demand_parasitic))  # [kWh/FU]

        # Calculate heat displacement
        heat_produced = energy_produced * efficiency_heat  # [kWh/FU]

        # Economic requirements
        CAPEX = get_CHP_CAPEX_distribution()
        o_and_m_costs = get_operation_and_maintenance_cost(CAPEX.values)

        # Initialise Requirements object and add requirements
        CHP_requirements = Requirements(name=self.name)
        CHP_requirements.add_requirement(Heat(values=heat_produced, name="Heat production by CHP",
                                              source=displaced_heat_source, generated=True))
        CHP_requirements.add_requirement(Electricity(values=electricity_produced, name="Electricity production by CHP",
                                                     generated=True))
        CHP_requirements.add_requirement(CAPEX)
        CHP_requirements.add_requirement(AnnualValue(name="O&M Costs CHP",
                                                     short_label="O&M CHP",
                                                     values=o_and_m_costs,
                                                     tag="O&M"))
        # Add requirements to object
        self.add_requirements(CHP_requirements)
