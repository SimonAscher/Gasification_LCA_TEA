# %% Import shared packages
import numpy as np

from functions.LCA import process_GWP_MC_to_df

# %% Milling and pelleting
from processes.pretreatment import milling_GWP_MC, pelleting_GWP_MC

milling_GWP = process_GWP_MC_to_df(milling_GWP_MC())
pelleting_GWP = process_GWP_MC_to_df(pelleting_GWP_MC())

print("Mean GWP milling:", np.mean(milling_GWP.loc["GWP"]["Milling"]))
# %% Drying
from processes.pretreatment import drying_GWP, drying_GWP_MC
from processes.pretreatment.utils import energy_drying

mass = 1000  # [kg]
moist_ar = 20  # moisture content as a fraction of feedstock on an as received basis
moist_post = 12  # desired final moisture content as a fraction

energy_drying_output_default = energy_drying(mass_feedstock=mass, moisture_ar=moist_ar,
                                             moisture_post_drying=moist_post,
                                             dryer_type='Direct fired dryer',
                                             specific_heat_reference_temp='40 degC',
                                             electricity_reference='GaBi (mean)',
                                             output_unit='kWh', syngas_as_fuel=False, show_values=False)

energy_drying_output = energy_drying(dryer_type='Direct fired dryer',
                                     specific_heat_reference_temp='40 degC', electricity_reference='GaBi (mean)',
                                     output_unit='kWh', syngas_as_fuel=False, show_values=False)

energy_drying_output_belt_dryer = energy_drying(dryer_type='Direct fired dryer',
                                     specific_heat_reference_temp='40 degC', electricity_reference='Huber Belt dryer',
                                     output_unit='kWh', syngas_as_fuel=False, show_values=False)

GWP_drying_example_1 = drying_GWP(energy_drying_output_default)
GWP_drying_example_2 = drying_GWP(energy_drying_output)
GWP_drying_example_3 = drying_GWP(energy_drying_output_belt_dryer)

# Monte Carlo
drying_GWP = process_GWP_MC_to_df(drying_GWP_MC())
