from functions.TEA.CAPEX_estimation import get_gasification_and_gas_cleaning_CAPEX_distributions, get_CHP_CAPEX_distribution
from functions.TEA.CAPEX_estimation import get_milling_CAPEX_distribution, get_shredding_CAPEX_distribution, get_pellet_mill_and_cooler_CAPEX_distribution, get_dryer_CAPEX_distribution

# Check gasification and CHP CAPEX
gasification_gas_cleaning_CAPEX = get_gasification_and_gas_cleaning_CAPEX_distributions()
CHP_CAPEX = get_CHP_CAPEX_distribution()

# Test pretreatment functions
a = get_milling_CAPEX_distribution()
b = get_shredding_CAPEX_distribution()
c = get_pellet_mill_and_cooler_CAPEX_distribution()
d = get_dryer_CAPEX_distribution()
