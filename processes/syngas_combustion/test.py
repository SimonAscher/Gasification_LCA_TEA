# # Test function
from functions.general.pred_to_dist import get_all_prediction_distributions
from models.prediction_model import get_models, make_predictions
from processes.syngas_combustion import syngas_combustion_GWP

fake_test_data_array = [49.09, 6.06, 0.08, 4, 5.88, 11.53, 800, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]

# Get models and make predictions with them
models = get_models()
all_predictions = make_predictions(models_dict=models, data=fake_test_data_array)

# Turn predictions into distributions
all_pred_dists = get_all_prediction_distributions(all_predictions)

# Calculate GWPs
GWP_results, detailed_emissions_dict = syngas_combustion_GWP(all_pred_dists)

# Show GWP as histogram
import matplotlib.pyplot as plt

plt.hist(GWP_results)
plt.show()
