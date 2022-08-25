# %% Test subfunctions
import time
from functions.general.pred_to_dist.utils import get_correct_sigma, make_dist

prediction = 3.8
output_label = "C2Hn [vol.% db]"
print(get_correct_sigma(prediction, output_label))

a = make_dist(mean=2, sigma=0.5, dist_type="gaussian")
b = make_dist(mean=2, sigma=0.5, dist_type="gausian")
print("a:", a)
print("b", b)

# %% Test main function

from functions.general.pred_to_dist import pred_to_dist

dist = pred_to_dist(prediction, output_label)
print("distribution:", dist)

# %% Test speed

import numpy as np

iterations = 10000
predictions = np.random.default_rng().normal(loc=12, scale=0.5, size=iterations)  # create fake predictions
prediction_distributions = []  # initialise list of prediction distributions
start = time.time()
for prediction in predictions:
    prediction_distributions.append(pred_to_dist(prediction, output_label))
end = time.time()
print("The time of execution of above program is :", end-start)