# %% Import shared packages
import numpy as np
from processes.pretreatment import FeedstockMilling, FeedstockPelleting
from processes.pretreatment import FeedstockDrying, FeedstockBaleShredding
from processes.pretreatment.utils import energy_drying
# %% Milling and pelleting
milling_GWP = FeedstockMilling()
pelleting_GWP = FeedstockPelleting()
print("Mean GWP milling:", milling_GWP.GWP_mean, "kg CO2 eq./FU")

# %% Drying
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
                                                specific_heat_reference_temp='40 degC',
                                                electricity_reference='Huber Belt dryer',
                                                output_unit='kWh', syngas_as_fuel=False, show_values=False)

GWP_drying_example_1 = FeedstockDrying(instantiate_with_default_reqs=False)
GWP_drying_example_1.calculate_requirements(energy_drying_dict=energy_drying_output_default)
GWP_drying_example_1.calculate_GWP()

GWP_drying_example_2 = FeedstockDrying(instantiate_with_default_reqs=False)
GWP_drying_example_2.calculate_requirements(energy_drying_dict=energy_drying_output)
GWP_drying_example_2.calculate_GWP()

GWP_drying_example_3 = FeedstockDrying(instantiate_with_default_reqs=False)
GWP_drying_example_3.calculate_requirements(energy_drying_dict=energy_drying_output_belt_dryer)
GWP_drying_example_3.calculate_GWP()

# Feedstock bale shredding
GWP_shredding = FeedstockBaleShredding()