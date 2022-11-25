from processes.carbon_capture import carbon_capture_GWP_MC
import numpy as np


# Get results
VPSA_results = carbon_capture_GWP_MC()
amine_results = carbon_capture_GWP_MC(cc_method="Amine post comb")

# Compare results
VPSA_mean_GWP = []
amine_mean_GWP = []

for _, count in enumerate(np.arange(len(VPSA_results.simulation_results))):
    VPSA_mean_GWP.append(VPSA_results.simulation_results[count].GWP)
    amine_mean_GWP.append(amine_results.simulation_results[count].GWP)

print("VPSA mean:", np.mean(VPSA_mean_GWP))
print("Amine process mean:", np.mean(amine_mean_GWP))
