# Get process models
import numpy as np

from processes.feedstock_drying import drying_GWP_MC
from processes.CHP import CHP_GWP_MC
from processes.gasification import gasification_GWP_MC
from processes.syngas_combustion import syngas_combustion_GWP_MC
from processes.biochar_soil_application import biochar_soil_GWP_MC
from processes.carbon_capture import carbon_capture_GWP_MC
from functions.LCA import process_GWP_MC_to_df, combine_GWP_dfs
from functions.LCA import plot_average_GWP_byprocess, plot_global_GWP, plot_single_process_GWP,\
    plot_global_GWP_byprocess
from functions.LCA import electricity_GWP, thermal_energy_GWP



# Set up dataframe to store results
# Get individual dataframes
df_1 = process_GWP_MC_to_df(CHP_GWP_MC())
df_2 = process_GWP_MC_to_df(drying_GWP_MC())
df_3 = process_GWP_MC_to_df(gasification_GWP_MC())
df_4 = process_GWP_MC_to_df(syngas_combustion_GWP_MC())
df_5 = process_GWP_MC_to_df(biochar_soil_GWP_MC())
df_6 = process_GWP_MC_to_df(carbon_capture_GWP_MC())

# Get overall dataframe
summary_df = combine_GWP_dfs((df_1, df_2, df_3, df_4, df_5, df_6))

# Create plots
global_plot = plot_global_GWP(summary_df)
avg_plot = plot_average_GWP_byprocess(summary_df, short_labels=True)
individual_plot = plot_single_process_GWP(summary_df, process_name="CHP")
individual_plot2 = plot_single_process_GWP(summary_df, process_name="Gasification", show_total=False)
individual_plot3 = plot_single_process_GWP(summary_df, process_name="Carbon Capture", show_total=False)

global_byprocess_plot = plot_global_GWP_byprocess(summary_df)


#%% Compare my results to Yi Fang's
# Compare results
CHP_mean_GWP = []
CHP_mean_GWP_ele = []
CHP_mean_GWP_heat = []

CHP_results = CHP_GWP_MC()
for _, count in enumerate(np.arange(len(CHP_results.simulation_results))):
    CHP_mean_GWP.append(CHP_results.simulation_results[count].GWP)
    CHP_mean_GWP_ele.append(CHP_results.simulation_results[count].subprocess_GWP[0])
    CHP_mean_GWP_heat.append(CHP_results.simulation_results[count].subprocess_GWP[1])


print("Overall system GWP mean:", np.mean(summary_df.loc["GWP"]["Total"]))
print("CHP mean:", np.mean(CHP_mean_GWP))
print("CHP mean electricity:", np.mean(CHP_mean_GWP_ele))
print("CHP mean heat:", np.mean(CHP_mean_GWP_heat))
print("GWP of 800 kWh electricity:", electricity_GWP(800))
print("GWP of 1,350 kWh heat:", thermal_energy_GWP(1350))

"""
800 kWh electricity (0.8 MWh) produced per FU
1350 kWh heat (1.35 MWh) produced per FU
Current GWP with carbon capture: -2200 kg CO2eq/FU

so for 1 MWh of electricity: -1760 kg CO2eq/MWh el.
"""