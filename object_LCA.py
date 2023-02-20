from processes.CHP import CHP_GWP_MC
from processes.gasification import gasification_GWP_MC
from processes.gasification import Gasification
from processes.CHP import CombinedHeatPower

from processes.syngas_combustion import SyngasCombustion

from functions.LCA import process_GWP_MC_to_df, combine_GWP_dfs, absorb_process_df

# CHP
CHP_old = CHP_GWP_MC()
CHP_df = process_GWP_MC_to_df(CHP_old)
CHP_new = CombinedHeatPower()

# Gasification
gasification_old = gasification_GWP_MC()
gasification_df = process_GWP_MC_to_df(gasification_old)
gasification_new = Gasification()

# Process with subprocess
syngas_combustion_new = SyngasCombustion()
CHP_new.add_subprocess(syngas_combustion_new)
CHP_new.calculate_GWP(consider_subprocesses=True)  # manually update GWP of overall object


