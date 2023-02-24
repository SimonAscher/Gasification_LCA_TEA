import numpy as np

from processes.CHP import CombinedHeatPower
from processes.gasification import Gasification
from processes.syngas_combustion import SyngasCombustion
from processes.biochar_soil_application import BiocharSoilApplication
from processes.carbon_capture import CarbonCapture
from processes.pretreatment import FeedstockDrying, FeedstockPelleting, FeedstockMilling, FeedstockBaleShredding
from configs.result_objects import Results
from configs.process_objects import Process
from functions.LCA import electricity_GWP, thermal_energy_GWP

# Create processes

# CHP
CHP_new = CombinedHeatPower()
CHP_new.add_subprocess(SyngasCombustion())  # add subprocess

# Gasification
gasification_new = Gasification()

# Biochar
biochar_new = BiocharSoilApplication()

# Carbon Capture
carbon_capture_new = CarbonCapture()

# Pretreatment
pretreatment_new = Process(name="Pretreatment", short_label="Pre.", instantiate_with_default_reqs=False)
pretreatment_new.add_subprocess(FeedstockDrying())
pretreatment_new.add_subprocess(FeedstockPelleting())
pretreatment_new.add_subprocess(FeedstockMilling())
pretreatment_new.add_subprocess(FeedstockBaleShredding())

# Plot individual processes
CHP_new.plot_GWP()
pretreatment_new.plot_GWP()

# Results object
example_results = Results(processes=(CHP_new, gasification_new, biochar_new, carbon_capture_new, pretreatment_new))
example_results.calculate_total_GWP()

# # Plot results
# example_results.plot_global_GWP()
# example_results.plot_average_GWP_byprocess()
# example_results.plot_global_GWP_byprocess()
example_results.save_report(r"C:\Users\2270577A\OneDrive - University of Glasgow\Desktop\LCA_report")


#%% Compare my results to Yi Fang's
# Compare results
CHP_mean_GWP = CHP_new.GWP_mean
CHP_mean_GWP_ele = np.mean(CHP_new.requirements[0].electricity[0].values)
CHP_mean_GWP_heat = np.mean(CHP_new.requirements[0].heat[0].values)

print("Overall system GWP mean:", example_results.GWP_mean, "kg CO2 eq.")
print("CHP GWP mean:", CHP_mean_GWP, "kg CO2 eq.")
print("CHP mean electricity:", CHP_mean_GWP_ele, "kWh")
print("CHP mean heat:", CHP_mean_GWP_heat, "kWh")
print("GWP of 800 kWh electricity:", electricity_GWP(800))
print("GWP of 1,300 kWh heat:", thermal_energy_GWP(1300))

"""
800 kWh electricity (0.8 MWh) produced per FU
1300 kWh heat (1.3 MWh) produced per FU
Current GWP with carbon capture: -1600 kg CO2eq/FU

so for 1 MWh of electricity: -2,000 kg CO2eq/MWh el.
"""
