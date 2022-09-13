# Test to_MC_array function
from functions.general.utility._to_MC_array import to_MC_array

a = to_MC_array(3.3)
print(to_MC_array(3.3))
print(to_MC_array(3.3, 5.5))

# Test scale_gas_fractions function
from functions.general.utility._scale_gas_fractions import scale_gas_fractions
import numpy as np

b = np.array([20, 10, 30, 20, 5, 8])
scaled_fractions_perc = scale_gas_fractions(b, gas_fractions_format="percentages")
scaled_fractions_dec = scale_gas_fractions(b, gas_fractions_format="decimals")
