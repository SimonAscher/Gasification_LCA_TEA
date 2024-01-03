# deprecated - now done in full_case_study jupyter notebook

from analysis.optimisation.helpers import (plot_optimisation_by_sets, plot_optimisation_by_parameter,
                                           load_and_analyse_results)

filepath_forestry_residues = "data/user_inputs_case_study_scotland_forestry_residues_optimisation/optimisation_results_make-entire-foreign-life"
filepath_draff = "data/user_inputs_case_study_scotland_draff_optimisation/optimisation_results_move-die-financial-service"
filepath_barley_straw = "data/user_inputs_case_study_scotland_barley_straw_optimisation/optimisation_results_ask-read-small-life"
plot_optimisation_by_sets(relative_results_objects_paths=[filepath_forestry_residues, filepath_draff, filepath_barley_straw],
                          set_labels=["Forestry Residues", "Draff", "Barley Straw"])

plot_optimisation_by_parameter(relative_results_objects_path=filepath_forestry_residues,
                               highlighted_parameter="gasification_temperature")

results, GWP_optimal, BCR_optimal, parameter_combinations_optimal = load_and_analyse_results(filepath_forestry_residues)