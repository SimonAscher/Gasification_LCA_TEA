import os
import pathlib
import warnings

import dill as pickle
import matplotlib.pyplot as plt
import numpy as np

from human_id import generate_id
from sklearn.model_selection import ParameterGrid
from matplotlib.cm import get_cmap
from itertools import compress
from numpy.typing import ArrayLike

from config import settings
from functions.MonteCarloSimulation import run_simulation


def get_pareto_mask(costs_array):
    """
    Helper function used across plotting functions. Gets pareto mask for the case where BCR is to be maximised and
    the negative value of GWP is to be maximised.

    Parameters
    ----------
    costs_array: ArrayLike
        Array of [i, j] (n_datapoints, n_costs) where  i is the number of GWP and BCR values and j=2 (i.e. BCR and GWP).
    """
    pareto_efficient_mask = np.ones(costs_array.shape[0], dtype=bool)

    for count, cost in enumerate(costs_array):  # find pareto optimal values
        pareto_efficient_mask[count] = (np.all(np.any(costs_array[:count] < cost, axis=1)) and
                                        np.all(np.any(costs_array[count + 1:] < cost, axis=1)))

    return pareto_efficient_mask


def run_optimisation(optimisation_parameters=None):
    """
    Run optimisation based on user_input file currently defined in config.py.
    It is highly recommended to set number of Monte Carlo iterations to 100 in user_input file to speed up optimisation.

    Parameters
    ----------
    optimisation_parameters: dict | None
        Dictionary of parameters which are to be varied during optimisation.
    """
    # General parameters
    reduced_MC_iterations = 100  # so that model runs faster
    results = []

    # Default optimisation parameters
    if optimisation_parameters is None:
        # optimisation_parameters = {"gasification_temperature": [650, 750, 850],
        #                            "ER": [0.25, 0.3],
        #                            "gasifying_agent": ["Air", "Steam"],
        #                            "operation_scale": ["Pilot", "Lab"],
        #                            "reactor_type": ["Fluidised bed", "Fixed bed"],
        #                            "rate_of_return_decimals": [0.04, 0.05, 0.06],
        #                            "carbon_capture": [True, False],
        #                            "carbon_tax": [0, 50, 75],
        #                            "system_life_span": [15, 20, 25]
        #                            "electricity_price": []
        #                            }
        optimisation_parameters = {"gasification_temperature": [700, 800, 900, 1000, 1100, 1200],
                                   "gasifying_agent": ["Air", "Steam"],
                                   "reactor_type": ["Fluidised bed", "Fixed bed"],
                                   "carbon_capture": [True, False],
                                   "carbon_tax": [0, 50, 75],
                                   }



    optimisation_combinations = list(ParameterGrid(optimisation_parameters))
    print(f"Run optimisation using the following feedstock: {settings.user_inputs.feedstock.name}")
    print(f"Number of combinations considered in optimisation: {len(optimisation_combinations)}")

    # Reduce number of Monte Carlo iterations to speed up model
    settings.user_inputs.general.MC_iterations = reduced_MC_iterations

    # Optimisation loop
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        for count, parameter_combination in enumerate(optimisation_combinations):
            # Overwrite instances in settings object
            if "gasification_temperature" in parameter_combination:
                settings.user_inputs.process_conditions["gasification_temperature"] = parameter_combination["gasification_temperature"]
            if "ER" in parameter_combination:
                settings.user_inputs.process_conditions["ER"] = parameter_combination["ER"]
            if "gasifying_agent" in parameter_combination:
                settings.user_inputs.process_conditions["gasifying_agent"] = parameter_combination["gasifying_agent"]
            if "operation_scale" in parameter_combination:
                settings.user_inputs.process_conditions["operation_scale"] = parameter_combination["operation_scale"]
            if "reactor_type" in parameter_combination:
                settings.user_inputs.process_conditions["reactor_type"] = parameter_combination["reactor_type"]
                # Updated bed material based on reactor type
                if settings.user_inputs.process_conditions["reactor_type"] == "Fluidised bed":
                    settings.user_inputs.process_conditions["bed_material"] = "Silica"
                elif settings.user_inputs.process_conditions["reactor_type"] == "Fixed bed":
                    settings.user_inputs.process_conditions["bed_material"] = "N/A"
            if "rate_of_return_decimals" in parameter_combination:
                settings.user_inputs.economic["rate_of_return_decimals"] = parameter_combination["rate_of_return_decimals"]
            if "system_life_span" in parameter_combination:
                settings.user_inputs.general["system_life_span"] = parameter_combination["system_life_span"]
            if "carbon_capture" in parameter_combination:
                settings.user_inputs.processes.carbon_capture["included"] = parameter_combination["carbon_capture"]
                settings.user_inputs.processes.carbon_capture["method"] = "VPSA post combustion"
                settings.user_inputs.economic["CO2_transport_price_choice"] = "default"
                settings.user_inputs.economic["CO2_storage_price_choice"] = "default"
            if "carbon_tax" in parameter_combination:
                settings.user_inputs.economic["carbon_tax_included"] = True
                settings.user_inputs.economic["carbon_tax_choice"] = "default"
                settings.user_inputs.economic.carbon_tax_parameters["value"] = parameter_combination["carbon_tax"]
                settings.user_inputs.economic.carbon_tax_parameters["distribution_type"] = "fixed"
            if "electricity_price" in parameter_combination:
                settings.user_inputs.economic["electricity_price_choice"] = "user selected"
                if parameter_combination["electricity_price"] is list:  # nested list denotes triangular distribution
                    settings.user_inputs.economic.electricity_price_parameters["lower"] = parameter_combination["electricity_price"][0]
                    settings.user_inputs.economic.electricity_price_parameters["mode"] = parameter_combination["electricity_price"][1]
                    settings.user_inputs.economic.electricity_price_parameters["upper"] = parameter_combination["electricity_price"][2]
                    settings.user_inputs.economic.electricity_price_parameters["distribution_type"] = "triangular"
                else:  # int or float denotes singular fixed value
                    settings.user_inputs.economic.electricity_price_parameters["value"] = parameter_combination["electricity_price"]
                    settings.user_inputs.economic.electricity_price_parameters["distribution_type"] = "fixed"
                    # Check that values are of the expected type
                    if isinstance(parameter_combination["electricity_price"], int) or isinstance(parameter_combination["electricity_price"], float):
                        raise ValueError("Decimal or integer expected.")

            settings.user_inputs.general.MC_iterations = reduced_MC_iterations

            result = run_simulation(show_figures=False)
            result.parameter_combination = parameter_combination
            results.append(result)

            print(f"Results for simulation run {count+1}:")
            print(f"Mean GWP: {results[count].GWP_mean}")
            print(f"Mean BCR: {results[count].BCR_mean}")

    # Store optimisation results

    # Generate paths for storage

    # Get other info
    ID = generate_id()
    user_inputs_settings_file_name = pathlib.PurePath(settings.settings_file[-1]).name

    # Get path components
    file_name = "optimisation_results_" + ID
    new_directory_name = user_inputs_settings_file_name[: user_inputs_settings_file_name.find('.')]

    # Add new directory to data folder
    try:
        os.mkdir(os.path.join("examples/data", new_directory_name))
    except OSError as error:
        warnings.warn(str(error))

        # Get path
    relative_results_objects_path = os.path.join("examples/data", new_directory_name, file_name)

    # Store results and parameter combinations
    with open(relative_results_objects_path, "wb") as f:
        pickle.dump(results, f)

    return results, relative_results_objects_path, optimisation_combinations


def load_and_analyse_results(relative_file_path):

    # Load results
    with open(relative_file_path, 'rb') as results_objects:
        results = (pickle.load(results_objects))

    # Get pareto optimal mask
    # Extract mean GWP, BCR, and parameter combination values for all data
    GWP_means = [results[i].GWP_mean for i in range(len(results))]
    BCR_means = [results[i].BCR_mean for i in range(len(results))]
    parameter_combinations = [results[i].parameter_combination for i in range(len(results))]

    # Turn values into np arrays to find pareto optimal values
    GWP_means = np.array(GWP_means)
    GWP_inverted = GWP_means * -1  # invert GWP values for optimisation - now want to maximise GWP and BCR
    BCR_means = np.array(BCR_means)
    parameter_combinations = np.array(parameter_combinations)

    # Get pareto optimal masks
    costs_array = np.array([BCR_means, GWP_inverted]).transpose()  # of dimension n_datapoints, n_costs
    pareto_efficient_mask = get_pareto_mask(costs_array)
    # pareto_inefficient_mask = np.invert(pareto_efficient_mask)

    # Get optimal values
    GWP_optimal = GWP_means[pareto_efficient_mask]
    BCR_optimal = BCR_means[pareto_efficient_mask]
    parameter_combinations_optimal = parameter_combinations[pareto_efficient_mask]

    # # Sort values
    GWP_optimal_sorted_indices = GWP_optimal.argsort()
    GWP_optimal = GWP_optimal[GWP_optimal_sorted_indices]
    BCR_optimal = BCR_optimal[GWP_optimal_sorted_indices]
    parameter_combinations_optimal = parameter_combinations_optimal[GWP_optimal_sorted_indices]

    print("Pareto optimal values and their corresponding parameter combinations:")
    for i in range(len(GWP_optimal)):
        print(f"{i+1} Optimum: \t GWP: {GWP_optimal[i]} \t  BCR: {BCR_optimal[i]} \t  Parameters: {parameter_combinations_optimal[i]}")

    return results, GWP_optimal, BCR_optimal, parameter_combinations_optimal


def plot_optimisation_by_sets(relative_results_objects_paths, set_labels=None):
    """
    Plots optimisation results for each set defined in relative_results_objects_paths.
    Typically, sets may consider different feedstocks.

    Parameters
    ----------
    relative_results_objects_paths: str | list
        File paths to the results objects which are to be plotted.
    set_labels: list[str] | None
        Set of labels describing the datasets defined by the file paths to the results objects.
    """
    # Get paths to results in right format
    results_object_paths = []
    if isinstance(relative_results_objects_paths, str):
        results_object_paths.append(relative_results_objects_paths)
    elif isinstance(relative_results_objects_paths, list):
        results_object_paths = relative_results_objects_paths
    else:
        raise ValueError("Wrong data type supplied.")

    # Define general parameters
    colour_map = get_cmap("Paired")
    colours = colour_map.colors
    scatter_colours = [colours[i] for i in range(len(colours)) if i % 2 == 0]
    pareto_front_colours = [colours[i] for i in range(len(colours)) if i % 2 != 0]
    if set_labels is None:
        set_labels = [(n+1) for n in range(len(relative_results_objects_paths))]

    # Load all sets of results
    result_sets = []
    for iteration in range(len(results_object_paths)):
        with open(results_object_paths[iteration], 'rb') as results_objects:
            result_sets.append(pickle.load(results_objects))

    # Extract mean GWP and BCR values of all data
    GWP_means_all = []
    BCR_means_all = []
    for set_no in result_sets:
        for results_instance in set_no:
            GWP_means_all.append(results_instance.GWP_mean)
            BCR_means_all.append(results_instance.BCR_mean)

    # Extract data for each set and plot
    for count, set_no in enumerate(result_sets):
        GWP_means = []
        BCR_means = []
        for results_instance in set_no:
            GWP_means.append(results_instance.GWP_mean)
            BCR_means.append(results_instance.BCR_mean)

        # Turn values into np arrays to find pareto optimal values
        GWP_means = np.array(GWP_means)
        GWP_inverted = GWP_means * -1  # invert GWP values for optimisation - now want to maximise GWP and BCR
        BCR_means = np.array(BCR_means)

        # Get pareto optimal values
        costs_array = np.array([BCR_means, GWP_inverted]).transpose()  # of dimension n_datapoints, n_costs
        pareto_efficient_mask = get_pareto_mask(costs_array)
        pareto_inefficient_mask = np.invert(pareto_efficient_mask)

        # Plot
        if count == 0:
            fig, ax = plt.subplots(dpi=300)
        ax.scatter(BCR_means[pareto_inefficient_mask], GWP_means[pareto_inefficient_mask],
                   label=f"Non-optimal solutions - {set_labels[count]}",
                   color=scatter_colours[count], alpha=0.5)
        ax.scatter(BCR_means[pareto_efficient_mask], GWP_means[pareto_efficient_mask],
                   label=f"Optimal solutions - {set_labels[count]}",
                   color=pareto_front_colours[count], zorder=9)

        # Get sorted arrays to plot pareto front
        BCR_pareto = BCR_means[pareto_efficient_mask]
        GWP_pareto = GWP_means[pareto_efficient_mask]
        BCR_pareto_sorted = sorted(BCR_pareto)
        GWP_pareto_sorted = [x for _, x in sorted(zip(BCR_pareto, GWP_pareto))]
        ax.plot(BCR_pareto_sorted, GWP_pareto_sorted, color=pareto_front_colours[count], zorder=10)

    # Add labels and display figure
    ax.set_xlabel("BCR")
    ax.set_ylabel("GWP " + settings.labels.LCA_output_plotting_string)
    ax.invert_yaxis()
    plt.legend().set_zorder(11)
    plt.tight_layout()
    plt.show()

    return fig, ax


def plot_optimisation_by_parameter(relative_results_objects_path, highlighted_parameter):
    """
    Plots optimisation results for a single set of results, but allows for differentiation by one parameter varied
    within the optimisation (e.g. ER, gasifying_agent, or carbon_capture ).

    Parameters
    ----------
    relative_results_objects_path: str
        File path to the results object which is to be plotted.
    highlighted_parameter: str
        Defines which optimisation parameter should be highlighted in plot. Can only highlight one parameter at a time.
    """
    # Define general parameters
    colour_map = get_cmap("Paired")
    colours = colour_map.colors
    parameter_colours = [colours[i] for i in range(len(colours)) if i % 2 == 0]

    # Load results
    with open(relative_results_objects_path, 'rb') as results_objects:
        results = (pickle.load(results_objects))

    # Get parameter combinations and masks
    parameter_combinations = [results[i].parameter_combination for i in range(len(results))]  # get dictionaries with parameter combinations
    parameter_values = [parameter_combinations[i][highlighted_parameter] for i in range(len(parameter_combinations))]  # get values for highlighted parameter
    parameter_options = list(set(parameter_values))
    parameter_options_str = [str(i) for i in parameter_options]

    parameter_masks = []
    for parameter_option in parameter_options:
        parameter_masks.append([i == parameter_option for i in parameter_values])

    # Extract mean GWP and BCR values of all data
    GWP_means = [results[i].GWP_mean for i in range(len(results))]
    BCR_means = [results[i].BCR_mean for i in range(len(results))]

    # Extract data for each set and plot
    for count, parameter_mask in enumerate(parameter_masks):
        GWP = list(compress(GWP_means, parameter_mask))
        BCR = list(compress(BCR_means, parameter_mask))

        if count == 0:
            fig, ax = plt.subplots(dpi=300)
        ax.scatter(BCR, GWP, label=f"{highlighted_parameter} = {parameter_options_str[count]}",
                   color=parameter_colours[count], alpha=0.5)

    # Overlay pareto front

    # Turn values into np arrays to find pareto optimal values
    GWP_means = np.array(GWP_means)
    GWP_inverted = GWP_means * -1  # invert GWP values for optimisation - now want to maximise GWP and BCR
    BCR_means = np.array(BCR_means)

    # Get pareto optimal values
    costs_array = np.array([BCR_means, GWP_inverted]).transpose()  # of dimension n_datapoints, n_costs
    pareto_efficient_mask = get_pareto_mask(costs_array)
    pareto_inefficient_mask = np.invert(pareto_efficient_mask)

    # Get sorted arrays to plot pareto front
    BCR_pareto = BCR_means[pareto_efficient_mask]
    GWP_pareto = GWP_means[pareto_efficient_mask]
    BCR_pareto_sorted = sorted(BCR_pareto)
    GWP_pareto_sorted = [x for _, x in sorted(zip(BCR_pareto, GWP_pareto))]

    # Plot pareto front
    ax.plot(BCR_pareto_sorted, GWP_pareto_sorted, label="Pareto front", color="black")

    # Add labels and display figure
    ax.set_xlabel("BCR")
    ax.set_ylabel("GWP " + settings.labels.LCA_output_plotting_string)
    ax.invert_yaxis()
    plt.legend()
    plt.tight_layout()
    plt.show()

    return fig, ax
