# %% Test Dynaconf and settings

# Import the settings settings from config.py
from config import settings

print(settings.background.iterations_MC)
print(settings.data.CO2_equivalents.electricity.UK)
print(settings.data.CO2_equivalents.electricity)

# %% Test some functions

from functions.general.pred_distributions.convenience_functions import pred_to_dist

test_label = settings.labels.output_data[1]
predictions_dist = pred_to_dist(12, test_label)
print(predictions_dist)

# %% Check if settings.toml works

test = (settings.data.biogenic_fractions)

test2 = settings.prediction_model
