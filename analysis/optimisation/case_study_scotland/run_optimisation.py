from analysis.optimisation.helpers import run_optimisation

optimisation_parameters = {"gasification_temperature": [650, 750, 850],
                          "ER": [0.25, 0.3],
                          "gasifying_agent": ["Air", "Steam"],
                          "operation_scale": ["Pilot", "Lab"],
                          "reactor_type": ["Fluidised bed", "Fixed bed"],
                          "rate_of_return_decimals": [0.04, 0.05, 0.06],
                          "carbon_capture": [True, False],
                          "carbon_tax": [0, 50, 75],
                          "system_life_span": [15, 20, 25],
                          "electricity_price": [0, 0.2, 0.3]  # TODO: edit and selected realistic values
                          }

results, relative_results_objects_path, optimisation_combinations = run_optimisation(optimisation_parameters)
