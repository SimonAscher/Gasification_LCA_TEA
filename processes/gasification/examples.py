from processes.gasification import gasification_requirements, gasification_GWP, gasification_GWP_MC
from processes.gasification.object_oriented_process import Gasification
from processes.gasification.utils import oxygen_for_stoichiometric_combustion, mass_agent
from processes.general import oxygen_rng_elect_req


oxygen_req = oxygen_for_stoichiometric_combustion()
default_example = mass_agent()
Steam_air_mixture_example = mass_agent(agent_type="Air + steam", air_fraction=0.4,
                                       steam_fraction=0.6)

# Steam example
Steam_mass_example = mass_agent(agent_type="Steam")
steam_test = gasification_requirements(agent_type="Steam", agent_mass=mass_agent(agent_type="Steam"))
test_steam_GWP = gasification_GWP(steam_test)
# Should be 77

# Oxygen example
oxygen_test = gasification_requirements(agent_type="Oxygen", agent_mass=mass_agent(agent_type="Oxygen"))
test_oxygen_GWP = gasification_GWP(oxygen_test)

# Test MC
MC_default = gasification_GWP_MC()

# Test object oriented approach
# Automated workflow
testObject = Gasification(instantiate_with_default_reqs=True)

# Manual workflow
testObject2 = Gasification(instantiate_with_default_reqs=False)
testObject2.calculate_requirements()
testObject2.calculate_GWP()
