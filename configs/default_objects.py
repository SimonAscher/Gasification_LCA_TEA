from collections import namedtuple


# Named tuple objects - used for making distributions for Monte Carlo simulation
triangular = namedtuple("triangular", "lower mode upper")
gaussian = namedtuple("gaussian", "mean sigma")

# TODO: Define and implement an object - could be dict, named tuple, class etc. to be used for all final LCA process
#  emissions results
