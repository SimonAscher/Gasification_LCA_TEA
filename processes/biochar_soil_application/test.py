# Test function
from functions.general.pred_distributions import get_all_prediction_distributions
from models.prediction_model import get_models, make_predictions
from processes.biochar_soil_application import biochar_soil_CO2_eq
from models.prediction_model import fetch_inputs


# Get models and make predictions with them
models = get_models()
all_predictions = make_predictions(models_dict=models, data=fetch_inputs())

# Turn predictions into distributions
all_pred_dists = get_all_prediction_distributions(all_predictions)

# Get biochar production prediction
biochar_yield = all_pred_dists["Char yield [g/kg wb]"]

# Calculate GWPs
GWP_results, detailed_emissions_dict = biochar_soil_CO2_eq(biochar_yield)

# Show GWP as histogram
import matplotlib.pyplot as plt

plt.hist(GWP_results)
plt.show()