# Get model predictions
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from models.prediction_model import get_models, make_predictions
from models.prediction_model import fetch_inputs

all_pred_dists = get_all_prediction_distributions(make_predictions(models_dict=get_models(), data=fetch_inputs()))

gas_supplied = all_pred_dists["Gas yield [Nm3/kg wb]"]
LHV_gas = all_pred_dists['LHV [MJ/Nm3]']

# Calculate GWP from energy displacement due to GWP
from processes.CHP import CHP_GWP


total_GWP, detailed_GWP = CHP_GWP(gas_supplied, LHV_gas)
