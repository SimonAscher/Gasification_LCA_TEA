from models.prediction_model import make_predictions
from models.prediction_model import get_models
from models.prediction_model import fetch_inputs

# Create data to make predictions on

# Create data frame with new data for Barley Straw

# Test function
fetched_models = get_models()
output = make_predictions(models_dict=fetched_models, data=fetch_inputs())
print(output)

output_reduced = make_predictions(models_dict=fetched_models, data=fetch_inputs(),
                                  output_selector=['CO [vol.% db]', 'CO2 [vol.% db]'])
print(output_reduced)
