from models.prediction_model import make_predictions
from models.prediction_model import get_models

# Create data to make predictions on

# Create data frame with new data for Barley Straw
test_data_array = [49.09, 6.06, 0.08, 4, 5.88, 11.53, 800, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]

# Test function
fetched_models = get_models()
output = make_predictions(models_dict=fetched_models, data=test_data_array)
print(output)

output_reduced = make_predictions(models_dict=fetched_models, data=test_data_array,
                                  output_selector=['CO [vol.% db]', 'CO2 [vol.% db]'])
print(output_reduced)
