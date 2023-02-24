# # Test function
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from models.prediction_model import get_models, make_predictions
from processes.syngas_combustion import SyngasCombustion


# Get models and make predictions with them
models = get_models()
all_predictions = make_predictions(models_dict=models)

# Turn predictions into distributions
all_pred_dists = get_all_prediction_distributions(all_predictions)

# Calculate GWPs
GWP_results = SyngasCombustion()
