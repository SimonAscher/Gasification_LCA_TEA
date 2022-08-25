# Test get_present_value function
from functions.TEA import get_present_value

future_value = 5000
print("Present value is:", get_present_value(future_value, "FV"))

# Test power_scale function
from functions.TEA import power_scale

print("Power scaled cost", power_scale(baseline_size=1000, design_size=800, baseline_cost=200000))
