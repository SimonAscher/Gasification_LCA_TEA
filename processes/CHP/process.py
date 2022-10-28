from config import settings
from functions.LCA import electricity_GWP, thermal_energy_GWP
import numpy as np


def CHP_GWP(gas_supplied, LHV_gas, displaced_heat_source="natural gas",
            efficiency_electrical=settings.data.conversion_efficiencies.CHP.SOFC["electrical"],
            efficiency_heat=settings.data.conversion_efficiencies.CHP.SOFC["heat"],
            demand_parasitic=settings.data.conversion_efficiencies.CHP.SOFC["parasitic"],
            FU=settings.general["FU"]):
    """

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
    FU: float
        Functional Unit.

    Returns
    -------

    """
    # Calculate amount of energy produced
    energy_production_rate = np.array(gas_supplied) * np.array(LHV_gas)  # [MJ/kg]
    energy_produced = energy_production_rate * FU  # [MJ/FU]

    # Calculate GWP due to electricity displacement
    electricity_out = (energy_produced * efficiency_electrical) * (1 - demand_parasitic) / 3.6  # [kWh/FU]
    GWP_electricity = electricity_GWP(electricity_out) * -1  # [kg CO2eq./FU]

    # Calculate GWP due to heat displacement
    heat_out = (energy_produced * efficiency_heat) / 3.6  # [kWh/FU]
    GWP_heat = thermal_energy_GWP(amount=heat_out, source=displaced_heat_source) * -1  # [kg CO2eq./FU]

    # Sum GWP
    GWP_total = list(GWP_electricity + GWP_heat)

    # Get detailed GWP results
    detailed_GWP = {"GWP CHP electricity": list(GWP_electricity), "GWP CHP thermal energy": list(GWP_heat),
                    "units": "kg CO2eq./FU"}

    return GWP_total, detailed_GWP
