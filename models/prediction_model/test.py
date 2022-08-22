from prediction_models import *
#  Create data to make predictions on

# Create data frame with new data for Barley Straw
test_data_array = [[49.09, 6.06, 0.08, 4, 5.88, 11.53, 800, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]]

# Test function
output = make_predictions(models_dict=get_models(),data=test_data_array)
