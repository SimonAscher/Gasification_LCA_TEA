from collections import namedtuple


# Named tuple objects - used for making distributions for Monte Carlo simulation
triangular = namedtuple("triangular", "lower mode upper")
gaussian = namedtuple("gaussian", "mean std")
