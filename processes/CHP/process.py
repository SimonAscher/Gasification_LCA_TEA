from config import settings
from functions.LCA import electricity_GWP, thermal_energy_GWP
import numpy as np
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from configs import process_GWP_output, process_GWP_output_MC


def CHP_GWP_MC(gas_supplied=get_all_prediction_distributions()["Gas yield [Nm3/kg wb]"],
            LHV_gas=get_all_prediction_distributions()['LHV [MJ/Nm3]'],
            displaced_heat_source="natural gas",
            efficiency_electrical=settings.data.conversion_efficiencies.CHP.SOFC["electrical"],
            efficiency_heat=settings.data.conversion_efficiencies.CHP.SOFC["heat"],
            demand_parasitic=settings.data.conversion_efficiencies.CHP.SOFC["parasitic"],
            FU=settings.general["FU"]):
    """
    Calculate the GWP of syngas use through CHP for all Monte Carlo runs.

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
    GWP_electricity = electricity_GWP(electricity_out, displaced=True)  # [kg CO2eq./FU]

    # Calculate GWP due to heat displacement
    heat_out = (energy_produced * efficiency_heat) / 3.6  # [kWh/FU]
    GWP_heat = thermal_energy_GWP(amount=heat_out, source=displaced_heat_source, displaced=True)  # [kg CO2eq./FU]

    # Sum GWP
    GWP_total = list(GWP_electricity + GWP_heat)

    # Initialise MC output object
    MC_outputs = process_GWP_output_MC(process_name="CHP")

    # Store values in default MC output object
    for count, entry in enumerate(GWP_total):
        GWP_object = process_GWP_output(process_name="CHP", GWP=entry)
        GWP_object.add_subprocess(name="Electricity displacement", GWP=GWP_electricity[count])
        GWP_object.add_subprocess(name="Thermal energy displacement", GWP=GWP_heat[count])

        MC_outputs.add_GWP_object(GWP_object)

    MC_outputs.subprocess_abbreviations = ("Elect.", "Heat", )  # add abbreviation of subprocess

    return MC_outputs
