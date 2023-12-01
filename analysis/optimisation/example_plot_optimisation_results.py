from helpers import plot_optimisation_by_sets, plot_optimisation_by_parameter

# plot_optimisation(relative_results_objects_paths=
#                   ["data\\user_inputs_Ascher_2019_Energy_181_optimisation\\optimisation_results_remember-environmental-case-house",
#                    "data\\user_inputs_Ascher_2019_Energy_181_optimisation\\optimisation_results_need-right-important-service",
#                    "data\\user_inputs_Ascher_2019_Energy_181_optimisation\\optimisation_results_serve-fine-information-country"
#                    ], set_labels=["Feed. Example 1", "Barley Straw", "Rice Straw"])

plot_optimisation_by_sets(
    relative_results_objects_paths='data\\user_inputs_Ascher_2019_Energy_181_optimisation\\optimisation_results_might-simple-nice-group')

plot_optimisation_by_parameter(
    relative_results_objects_path='data\\user_inputs_Ascher_2019_Energy_181_optimisation\\optimisation_results_might-simple-nice-group',
    highlighted_parameter="carbon_tax")

plot_optimisation_by_parameter(
    relative_results_objects_path='data\\user_inputs_Ascher_2019_Energy_181_optimisation\\optimisation_results_might-simple-nice-group',
    highlighted_parameter="carbon_capture")

plot_optimisation_by_parameter(
    relative_results_objects_path='data\\user_inputs_Ascher_2019_Energy_181_optimisation\\optimisation_results_might-simple-nice-group',
    highlighted_parameter="gasification_temperature")
