from functions.general.predictions_to_distributions import get_all_prediction_distributions
from models.prediction_model import get_models, make_predictions
from functions.general.utility import fetch_ML_inputs
from processes.biochar_soil_application.process import BiocharSoilApplication


# Get models and make predictions with them
models = get_models()
all_predictions = make_predictions(models_dict=models, data=[fetch_ML_inputs()])

# Turn predictions into distributions
all_pred_dists = get_all_prediction_distributions(all_predictions)

# Get biochar production prediction
biochar_yield = all_pred_dists["Char yield [g/kg wb]"]

# Calculate GWPs
test_obj = BiocharSoilApplication()
