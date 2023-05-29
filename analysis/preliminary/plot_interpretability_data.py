import pandas as pd

from config import settings
from functions.general import load_GBR_performance_summary_df
from functions.general.plotting import plot_SHAP_local_prediction, plot_GBR_scatter_all, combined_feat_imp_plot

# Plot combined scatter plot
model_data_df = load_GBR_performance_summary_df()
plot = plot_GBR_scatter_all(model_data_df, model_type="GBR", marker_style=".", save_fig=True)

# plot combined SHAP feature importance plot
plot2_a = combined_feat_imp_plot(performance_summary=model_data_df, model_type="gini", save=True,
                                 legend_style="short")
plot2_b = combined_feat_imp_plot(performance_summary=model_data_df, model_type="perm", save=True,
                                 legend_style="short")
plot2_c = combined_feat_imp_plot(performance_summary=model_data_df, model_type="shap", save=True,
                                 legend_style="short")

# Create individual plots for barley straw and MSW predictions
# %% Barley Straw Data

# Create data frame with new data for Barley Straw
barley_test_data_array = [[49.09, 6.06, 0.08, 4, 5.88, 11.53, 800, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                          # base case
                          [49.09, 6.06, 0.08, 4, 5.88, 11.53, 800, 1, 0.3, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
                          # steam
                          [49.09, 6.06, 0.08, 1, 5.88, 11.53, 800, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                          # low particle size
                          [49.09, 6.06, 0.08, 20, 5.88, 11.53, 800, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
                           1],  # high particle size
                          [49.09, 6.06, 0.08, 4, 5.88, 11.53, 600, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                          # low temperature
                          [49.09, 6.06, 0.08, 4, 5.88, 11.53, 1000, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
                           1],  # high temperature
                          [49.09, 6.06, 0.08, 4, 5.88, 20.00, 800, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                          # high moisture
                          ]
barley_test_df = pd.DataFrame(data=barley_test_data_array,
                              index=['Base', 'Steam', 'Low Particle Size', 'High Particle Size', 'Low Temperature',
                                     'High Temperature', 'High Moisture'],
                              columns=model_data_df.loc['x_train']['N2 [vol.% db]'].columns)

# All data taken from https://phyllis.nl/Biomass/View/3169 - other data is listed below - design choices for base case:
# particle size = 4 mm
# temperature = 800 deg C
# Operation = Continuous
# ER = 0.3
# Catalyst = None
# Scale = Pilot
# agent = air
# bed = fluidised bed
# bed material = silica

# Plot force plots
plot_SHAP_local_prediction(barley_test_df, target_name='Gas yield [Nm3/kg wb]', save=True, save_type='barley')

# %% MSW Data

# Create data frame with new data for MSW
MSW_test_data_array = [[59.19, 9.80, 0.29, 4, 16.82, 6.16, 800, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                       # base case
                       [59.19, 9.80, 0.29, 1, 16.82, 6.16, 800, 1, 0.3, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1],
                       # steam
                       [59.19, 9.80, 0.29, 1, 16.82, 6.16, 800, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                       # low particle size
                       [59.19, 9.80, 0.29, 20, 16.82, 6.16, 800, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                       # high particle size
                       [59.19, 9.80, 0.29, 4, 16.82, 6.16, 600, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                       # low temperature
                       [59.19, 9.80, 0.29, 4, 16.82, 6.16, 1000, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
                       # high temperature
                       [59.19, 9.80, 0.29, 4, 16.82, 6.16, 800, 1, 0.3, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0],
                       # batch and downdraft and steam
                       ]
MSW_test_df = pd.DataFrame(data=MSW_test_data_array,
                           index=['Base', 'Steam', 'Low Particle Size', 'High Particle Size', 'Low Temperature',
                                  'High Temperature', 'Batch, Downdraft, and Steam'],
                           columns=model_data_df.loc['x_train']['N2 [vol.% db]'].columns)

# All data taken from https://phyllis.nl/Biomass/View/2920 - other data is listed below - design choices for base case:
# particle size = 4 mm
# temperature = 800 deg C
# Operation = Continuous
# ER = 0.3
# Catalyst = None
# Scale = Pilot
# agent = air
# bed = fluidised bed
# bed material = silica

# Plot force plots
plot_SHAP_local_prediction(MSW_test_df, target_name='LHV [MJ/Nm3]', save=True, save_type='MSW')
