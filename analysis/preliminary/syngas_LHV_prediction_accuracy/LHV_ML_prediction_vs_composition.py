import os
import pickle
import matplotlib

import seaborn as sns
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from functions.general import calculate_syngas_LHV, MAPE
from functions.general.utility import get_project_root
from sklearn.metrics import mean_squared_error


#%%
# Load dataframe with models stored

# Get file path to GBR data
project_root = get_project_root()
full_file_path = str(project_root) + r"\data\GBR_performance_summary"

# Load performance summary object
perf_summary = pickle.load(open(full_file_path, "rb"))
current_directory = os.getcwd()


#%%
# Get true known LHV for test set
true_LHVs = np.array(perf_summary["LHV [MJ/Nm3]"].y_test)

# Get predictions
predictions_LHV = np.array(perf_summary["LHV [MJ/Nm3]"].test_predictions)
predictions_N2 = np.array(perf_summary["N2 [vol.% db]"].test_predictions)
predictions_H2 = np.array(perf_summary["H2 [vol.% db]"].test_predictions)
predictions_CO = np.array(perf_summary["CO [vol.% db]"].test_predictions)
predictions_CO2 = np.array(perf_summary["CO2 [vol.% db]"].test_predictions)
predictions_CH4 = np.array(perf_summary["CH4 [vol.% db]"].test_predictions)
predictions_C2Hn = np.array(perf_summary["C2Hn [vol.% db]"].test_predictions)

# Get calculated and Ml predicted LHVs
calculated_LHVs = []
ML_predicted_LHVs = []
print("Display data:")
for count in range(len(predictions_LHV)):
    input_dict = {"LHV [MJ/Nm3]": predictions_LHV[count],
                  "N2 [vol.% db]": predictions_LHV[count],
                  "H2 [vol.% db]": predictions_LHV[count],
                  "CO [vol.% db]": predictions_LHV[count],
                  "CO2 [vol.% db]": predictions_LHV[count],
                  "CH4 [vol.% db]": predictions_LHV[count],
                  "C2Hn [vol.% db]": predictions_LHV[count],
                  }
    syngas_LHV_comparison_dict = calculate_syngas_LHV(predictions=input_dict)
    syngas_LHV_comparison_dict["True LHV"] = true_LHVs[count]
    print(syngas_LHV_comparison_dict)

    ML_predicted_LHVs.append(syngas_LHV_comparison_dict["ML predicted LHV"])
    calculated_LHVs.append(syngas_LHV_comparison_dict["Calculated LHV"])

ML_predicted_RMSE = mean_squared_error(y_true=true_LHVs,
                                       y_pred=ML_predicted_LHVs, squared=False)
calculated_RMSE = mean_squared_error(y_true=true_LHVs,
                                     y_pred=calculated_LHVs, squared=False)

ML_predicted_MAPE = MAPE(y_true=true_LHVs, y_pred=ML_predicted_LHVs)
calculated_MAPE = MAPE(y_true=true_LHVs, y_pred=calculated_LHVs)

print()
print("ML predicted RMSE: {:.2f}".format(ML_predicted_RMSE))
print("Calculated predicted RMSE: {:.2f}".format(calculated_RMSE))
print("ML predicted MAPE: {:.2f} %".format(ML_predicted_MAPE))
print("Calculated predicted MAPE: {:.2f} %".format(calculated_MAPE))


#%%
fig1, ax1 = plt.subplots()
sns.set_theme()
x_axis = np.arange(len(true_LHVs))
ax1.scatter(x_axis, true_LHVs, color="black", label="True")
ax1.scatter(x_axis, ML_predicted_LHVs, color="green", label="ML predictions")
ax1.scatter(x_axis, calculated_LHVs, color="red", label="Calculated")
ax1.legend()
ax1.set_xlabel("Instance")
ax1.set_ylabel("Syngas LHV [MJ/m3]")
plt.show()

#%%  Histograms of absolute errors for test set
fig2, ax2 = plt.subplots()
sns.set(font_scale=1.5)
ML_absolute_errors = abs(np.array(ML_predicted_LHVs) - true_LHVs)
calculated_absolute_errors = abs(np.array(calculated_LHVs) - true_LHVs)
error_df = pd.DataFrame({"ML predictions": ML_absolute_errors,
                         "Calculated values": calculated_absolute_errors})
sns.histplot(error_df, alpha=0.5)
plt.xlabel(r"Absolute error [MJ/m$^{3}$]", fontsize=16)
plt.ylabel("Count", fontsize=16)
plt.tick_params(labelsize=16)
plt.tight_layout()
plt.savefig(current_directory + r"\\" + r"\figures" + r"\ML_predicted_vs_calculated_errors" + ".tiff", dpi=500,
            bbox_inches="tight")
plt.show()


#%%
fig3, ax3 = plt.subplots()
sns.set_theme()

ax3.plot(np.sort(ML_absolute_errors), color="green", label="ML predictions")
ax3.plot(np.sort(calculated_absolute_errors), color="red", label="Calculated values")
ax3.legend()
ax3.set_xlabel("Sorted instances")
ax3.set_ylabel("Absolute error[MJ/m3]")
plt.show()
