from functions.general.predictions_to_distributions import get_all_prediction_distributions
from functions.general.utility import fetch_ML_inputs
from models.prediction_model import get_models, make_predictions
from processes.CHP import CombinedHeatPower


ML_input_data = [fetch_ML_inputs()]
all_pred_dists = get_all_prediction_distributions(make_predictions(models_dict=get_models(), data=ML_input_data))

gas_supplied = all_pred_dists["Gas yield [Nm3/kg wb]"]
LHV_gas = all_pred_dists['LHV [MJ/Nm3]']

# Calculate GWP from energy displacement due to GWP
GWP_output = CombinedHeatPower()
