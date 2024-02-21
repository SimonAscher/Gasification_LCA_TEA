# deprecated - now done in full_case_study jupyter notebook

from analysis.optimisation.helpers import plot_optimisation_by_sets, plot_optimisation_by_parameter


filepath_forestry_residues = "data/user_inputs_case_study_scotland_forestry_residues_optimisation/optimisation_results_offer-wrong-school-lot"
filepath_draff = "data/user_inputs_case_study_scotland_draff_optimisation/optimisation_results_move-die-financial-service"
filepath_barley_straw = "data/user_inputs_case_study_scotland_barley_straw_optimisation/optimisation_results_ask-read-small-life"

plot_optimisation_by_sets(results_objects_paths=[filepath_forestry_residues, filepath_draff, filepath_barley_straw],
                          set_labels=["Forestry Residues", "Draff", "Barley Straw"])
# Plot forestry residues
plot_optimisation_by_parameter(results_object_path=filepath_forestry_residues,
                               highlighted_parameter="gasification_temperature")
plot_optimisation_by_parameter(results_object_path=filepath_forestry_residues, highlighted_parameter="ER")
plot_optimisation_by_parameter(results_object_path=filepath_forestry_residues, highlighted_parameter="gasifying_agent")
plot_optimisation_by_parameter(results_object_path=filepath_forestry_residues, highlighted_parameter="operation_scale")
plot_optimisation_by_parameter(results_object_path=filepath_forestry_residues, highlighted_parameter="reactor_type")
plot_optimisation_by_parameter(results_object_path=filepath_forestry_residues,
                               highlighted_parameter="rate_of_return_decimals")
plot_optimisation_by_parameter(results_object_path=filepath_forestry_residues, highlighted_parameter="carbon_capture")
plot_optimisation_by_parameter(results_object_path=filepath_forestry_residues, highlighted_parameter="carbon_tax")

# Plot draff
plot_optimisation_by_parameter(results_object_path=filepath_draff, highlighted_parameter="gasification_temperature")
plot_optimisation_by_parameter(results_object_path=filepath_draff, highlighted_parameter="ER")
plot_optimisation_by_parameter(results_object_path=filepath_draff, highlighted_parameter="gasifying_agent")
plot_optimisation_by_parameter(results_object_path=filepath_draff, highlighted_parameter="operation_scale")
plot_optimisation_by_parameter(results_object_path=filepath_draff, highlighted_parameter="reactor_type")
plot_optimisation_by_parameter(results_object_path=filepath_draff, highlighted_parameter="rate_of_return_decimals")
plot_optimisation_by_parameter(results_object_path=filepath_draff, highlighted_parameter="carbon_capture")
plot_optimisation_by_parameter(results_object_path=filepath_draff, highlighted_parameter="carbon_tax")

# Plot barlye straw
plot_optimisation_by_parameter(results_object_path=filepath_barley_straw,
                               highlighted_parameter="gasification_temperature")
plot_optimisation_by_parameter(results_object_path=filepath_barley_straw, highlighted_parameter="ER")
plot_optimisation_by_parameter(results_object_path=filepath_barley_straw, highlighted_parameter="gasifying_agent")
plot_optimisation_by_parameter(results_object_path=filepath_barley_straw, highlighted_parameter="operation_scale")
plot_optimisation_by_parameter(results_object_path=filepath_barley_straw, highlighted_parameter="reactor_type")
plot_optimisation_by_parameter(results_object_path=filepath_barley_straw,
                               highlighted_parameter="rate_of_return_decimals")
plot_optimisation_by_parameter(results_object_path=filepath_barley_straw, highlighted_parameter="carbon_capture")
plot_optimisation_by_parameter(results_object_path=filepath_barley_straw, highlighted_parameter="carbon_tax")


