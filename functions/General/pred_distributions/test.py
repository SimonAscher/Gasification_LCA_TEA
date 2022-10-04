# %% Test subfunctions
import time
from functions.general.pred_distributions.utils import get_correct_sigma
from functions.MC import make_dist

prediction = 3.8
output_label = "C2Hn [vol.% db]"
correct_sigma = get_correct_sigma(prediction, output_label)
print("Correct sigma:", correct_sigma)

from configs import gaussian

a = make_dist(gaussian(prediction, correct_sigma))

print("Distribution with separate functions:", a)

# %% Test main function

from functions.general.pred_distributions import pred_to_dist

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
from functions.general.pred_distributions import get_all_prediction_distributions
from models.prediction_model import get_models, make_predictions

fake_test_data_array = [49.09, 6.06, 0.08, 4, 5.88, 11.53, 800, 1, 0.3, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1]

models = get_models()
all_predictions = make_predictions(models_dict=models, data=fake_test_data_array)
all_pred_dists = get_all_prediction_distributions(all_predictions)
