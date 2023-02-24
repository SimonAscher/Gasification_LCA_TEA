from processes.gasification.process import Gasification
from processes.gasification.utils import oxygen_for_stoichiometric_combustion, mass_agent


oxygen_req = oxygen_for_stoichiometric_combustion()
default_example = mass_agent()
Steam_air_mixture_example = mass_agent(agent_type="Air + steam", air_fraction=0.4,
                                       steam_fraction=0.6)

# Steam example
Steam_mass_example = mass_agent(agent_type="Steam")

# Test object oriented approach
# Automated workflow
testObject = Gasification(instantiate_with_default_reqs=True)

# Manual workflow
testObject2 = Gasification(instantiate_with_default_reqs=False)
testObject2.calculate_requirements(agent_type="Air")
testObject2.calculate_GWP()

testObject3 = Gasification(instantiate_with_default_reqs=False)
testObject3.calculate_requirements(agent_type="Oxygen")
testObject3.calculate_GWP()
