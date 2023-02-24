from processes.carbon_capture import CarbonCapture
import numpy as np


# Get results
VPSA_results = CarbonCapture()
amine_results = CarbonCapture(instantiate_with_default_reqs=False)
amine_results.calculate_requirements(cc_method="Amine post comb")
amine_results.calculate_GWP()

# Compare resulte
print("VPSA mean:", np.mean(VPSA_results.GWP_mean), "kg CO2 eq./FU")
print("Amine process mean:", np.mean(amine_results.GWP_mean), "kg CO2 eq./FU")
