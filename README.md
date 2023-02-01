# Model for the environmental and economic analysis of biomass and waste gasification schemes
Repository containing a life cycle assessment (LCA) framework for the analysis of biomass and waste gasification schemes.
Models for techno-economic analysis (TEA) will be added at a later stage.

All processes have default options which the model will revert to if the user does not specify any other data.
User data is stored in 'configs/user_inputs.toml' A gui will be implemented at a later stage which will populate the 
.toml file with the specified user data.

# Life cycle assessment (LCA):
## Processes:
The processes folder contains process models for all subprocesses making up a gasification system. 
For the calculation of LCA results, process.py files contain functions to calculate a process' GWP. Processes may require any given number of helper functions, but two main function types are used to calculate GWP results:
1. `process_GWP` functions are used to calculate the GWP of a single combination of parameters. Their outputs are stored in `process_GWP_output` objects.
2. `process_GWP_MC` functions are used to calculate the GWP for a given number of Monte Carlo simulations. For this they will store `process_GWP_output` objects for each Monte Carlo simulation in a `process_GWP_output_MC` object.

_Note: As environmental and economic analysis will share data, this structure will be changed at a later stage to better integrate with the TEA._
