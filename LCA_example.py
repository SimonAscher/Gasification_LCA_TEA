from functions.MonteCarloSimulation import run_simulation

results = run_simulation()

# # Plot results
results_file = results.save_report(storage_path=r"C:\Users\2270577A\OneDrive - University of Glasgow\Desktop\LCA_report",
                                   save_figures=True)
