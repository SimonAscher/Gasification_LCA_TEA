from collections import namedtuple


# Named tuple objects - used for making distributions for Monte Carlo simulation
fixed_dist_maker = namedtuple("fixed_dist_maker", "value")
range_dist_maker = namedtuple("range_dist_maker", "low high")  # i.e. uniform distribution
triangular_dist_maker = namedtuple("triangular_dist_maker", "lower mode upper")
gaussian_dist_maker = namedtuple("gaussian_dist_maker", "mean std")
