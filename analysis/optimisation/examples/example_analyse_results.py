from analysis.optimisation.helpers import load_and_analyse_results

# Load results
filepath_forestry_residues = "data/user_inputs_case_study_scotland_forestry_residues_optimisation/optimisation_results_offer-wrong-school-lot"


results, GWP_optimal, BCR_optimal, parameter_combinations_optimal = load_and_analyse_results(filepath_forestry_residues)