# TODO: This code is currently very inefficient - if I want to make e.g. 1000 predictions the model would get loaded
#  every time - change so that models are extracted, and then just used to make predictions. Efficiency improvements
#  needed: Want model selector function separately - this way will be able to load from pickle object instead of having
#  to load big performance summary every time

