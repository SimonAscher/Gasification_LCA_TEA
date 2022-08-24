from functions.general.pred_to_dist.get_correct_sigma.get_correct_sigma import *

prediction = 3.8
output_label = "C2Hn [vol.% db]"
print(get_correct_sigma(prediction, output_label))

from functions.general.pred_to_dist.make_dist.make_dist import *

a = make_dist(mean=2, sigma=0.5, dist_type="gaussian")
b = make_dist(mean=2, sigma=0.5, dist_type="gausian")
print("a:", a)
print("b", b)

import pred_to_dist

dist = pred_to_dist.pred_to_dist(prediction, output_label)
print("distribution:", dist)
