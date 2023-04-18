# %% Test subfunctions
import time
from functions.general.predictions_to_distributions.utils import get_correct_sigma
from functions.MonteCarloSimulation import get_distribution_draws

prediction = 3.8
output_label = "C2Hn [vol.% db]"
correct_sigma = get_correct_sigma(prediction, output_label)
print("Correct sigma:", correct_sigma)

from objects import gaussian_dist_maker

a = get_distribution_draws(gaussian_dist_maker(prediction, correct_sigma))

print("Distribution with separate functions:", a)

# %% Test main function

from functions.general.predictions_to_distributions import pred_to_dist

dist = pred_to_dist(prediction, output_label)
print("Distribution with convenience function:", dist)

# %% Test speed

import numpy as np

iterations = 10
predictions = np.random.default_rng().normal(loc=12, scale=0.5, size=iterations)  # create fake predictions
prediction_distributions = []  # initialise list of prediction distributions
start = time.time()
for prediction in predictions:
    prediction_distributions.append(pred_to_dist(prediction, output_label))
end = time.time()
print("The time of execution of above program is :", end - start)

# %% Test func to get all predictions to distributions
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from models.prediction_model import get_models, make_predictions
from functions.general.utility import fetch_ML_inputs

models = get_models()
all_predictions = make_predictions(models_dict=models, data=fetch_ML_inputs())
all_pred_dists = get_all_prediction_distributions(all_predictions)
