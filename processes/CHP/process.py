import numpy as np

from dataclasses import dataclass
from config import settings
from configs.process_objects import Process
from configs.requirement_objects import Requirements, Heat, Electricity
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from functions.general.utility.unit_conversions import MJ_to_kWh


@dataclass()
class CombinedHeatPower(Process):
    name: str = "Combined heat and power (CHP)"
    short_label: str = "CHP"

    def instantiate_default_requirements(self):
        self.calculate_requirements()

    def calculate_requirements(self, gas_supplied=None, LHV_gas=None, displaced_heat_source=None,
                               efficiency_electrical=settings.data.conversion_efficiencies.CHP.SOFC["electrical"],
                               efficiency_heat=settings.data.conversion_efficiencies.CHP.SOFC["heat"],
                               demand_parasitic=settings.data.conversion_efficiencies.CHP.SOFC["parasitic"],
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

        # Calculate amount of energy produced
        energy_production_rate = np.array(gas_supplied) * np.array(LHV_gas)  # [MJ/kg]
        energy_produced = MJ_to_kWh(energy_production_rate * FU)  # [kWh/FU]

        # Calculate GWP due to electricity displacement
        electricity_produced = list((energy_produced * efficiency_electrical) * (1 - demand_parasitic))  # [kWh/FU]

        # Calculate GWP due to heat displacement
        heat_produced = energy_produced * efficiency_heat  # [kWh/FU]

        # Initialise Requirements object and add requirements
        CHP_requirements = Requirements(name=self.name)
        CHP_requirements.add_requirement(Heat(values=heat_produced, name="Heat production by CHP",
                                              source=displaced_heat_source, generated=True))
        CHP_requirements.add_requirement(Electricity(values=electricity_produced, name="Electricity production by CHP",
                                                     generated=True))

        # Add requirements to object
        self.add_requirements(CHP_requirements)
