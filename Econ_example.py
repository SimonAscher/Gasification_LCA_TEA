from functions.MonteCarloSimulation import run_simulation
from functions.MonteCarloSimulation import dist_maker_from_settings

results = run_simulation()
results.store_figures()

from config import settings
import numpy as np

electricity_consumptions = np.array(results.electricity_results["Component distributions"])
electricity_consumers = results.electricity_results["Component names"][0:min(electricity_consumptions.shape)]

electricity_requirement_array = results.processes[1].requirements[1].electricity[0].values

example_electricity_req = results.processes[1].requirements[1].electricity[0]





