# LCA and TEA Model
This repository contains the LCA and TEA model of my PhD

# Life cycle assessment (LCA):
## Processes:
The processes folder contains process models for all subprocesses making up a gasification system. 
For the calculation of LCA results, process.py files contain functions to calculate a process' GWP. Processes may require any given number of helper functions, but two main function types are used to calculate GWP results:
1. `process_GWP` functions are used to calculate the GWP of a single combination of parameters. Their outputs are stored in `process_GWP_output` objects.
2. `process_GWP_MC` functions are used to calculate the GWP for a given number of Monte Carlo simulations. For this they will store `process_GWP_output` objects for each Monte Carlo simulation in a `process_GWP_output_MC` object.
