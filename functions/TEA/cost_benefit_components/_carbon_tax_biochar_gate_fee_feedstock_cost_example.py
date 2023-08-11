from functions.MonteCarloSimulation import run_simulation
from functions.TEA.cost_benefit_components import carbon_tax_cost_benefit, biochar_sale_cost_benefit, gate_fee_or_feedstock_cost_benefit

results = run_simulation()

# # Plot results
results_file = results.save_report(storage_path=r"C:\Users\2270577A\OneDrive - University of Glasgow\Desktop\LCA_report",
                                   save_figures=True)

a = biochar_sale_cost_benefit()
b = carbon_tax_cost_benefit(results)
c = gate_fee_or_feedstock_cost_benefit()
