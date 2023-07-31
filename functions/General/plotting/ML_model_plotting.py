import pickle

import matplotlib
import os
import pandas as pd
import shap
import numpy as np
import matplotlib.pyplot as plt

from config import settings
from pandas import DataFrame
from dynaconf.utils.boxing import DynaBox
from functions.general import load_GBR_performance_summary_df
from functions.general.utility import get_project_root
from sklearn.preprocessing import normalize


# Define util/prerequisite functions used within the plotting functions:
def _scale_array(array, lower_bound=0, upper_bound=1):
    """
    Function to scale values in array to chosen range.

    Parameters
    ----------
    array
    lower_bound
    upper_bound

    Returns
    -------

    """
    scaled_array = lower_bound + (array - np.min(array)) / (np.max(array) - np.min(array)) * (upper_bound - lower_bound)
    return scaled_array


def _split_array(array):
    """
    Function that splits array in half.

    Parameters
    ----------
    array

    Returns
    -------

    """
    half = len(array) // 2
    first_half = array[:half]
    second_half = array[half:]
    return first_half, second_half


def plot_GBR_scatter_all(performance_summary, model_type, plot_style=None, marker_style='varied', save_fig=False):
    """
    Create scatter plot across all model outputs for test data only.

    Parameters
    ----------
    performance_summary: DataFrame
        Performance summary dataframe of the model which is to be plotted.
    model_type: str
        Used to save the figure. E.g. for Random Forest model: model_type = 'RF'.
    plot_style: DynaBox
        Defines the figure style (e.g. font size, figure size, etc.)
    marker_style: str
         Defines which markers should be used for scatter plot (default: 'varied') Change to 'o' for a neater looking
         plot but less distinction between points.
    save_fig: bool
        Specifies whether the model should be saved (default: False).
        Change to save_fig = True if figure should be saved.

    Returns
    -------
    """
    if plot_style is None:
        plot_style = settings.plotting.poster

    # Initialise Figure
    fig, ax = plt.subplots(figsize=tuple(plot_style.fig_size), dpi=plot_style.fig_dpi, tight_layout=True)

    if marker_style == 'varied':
        marker_styles = np.array(matplotlib.markers.MarkerStyle.filled_markers)
    else:
        marker_styles = np.array([marker_style] * performance_summary.columns.shape[0])

    # Loop to extract, scale, and plot values
    for column in np.arange(performance_summary.columns.shape[0]):
        # Extract predictions and targets
        predictions = performance_summary.iloc[:, column]['test_predictions']
        targets = np.array(performance_summary.iloc[:, column]['test_targets'])
        combined_array = np.concatenate((targets, predictions))  # combined to scale together
        scaled_array = _scale_array(combined_array)
        scaled_predictions, scaled_targets = _split_array(scaled_array)

        # Extract corresponding label and marker styles
        legend_label = np.array(performance_summary.columns)[column]

        marker = marker_styles[column]

        # Plot predictions vs. targets
        ax.scatter(scaled_targets, scaled_predictions, marker=marker, label=legend_label, s=plot_style.marker_size,
                   alpha=0.7, zorder=3)

    # Configure graph
    legend_1 = ax.legend([r'$N_{2}$',
                          r'$H_{2}$',
                          r'CO',
                          r'$CO_{2}$',
                          r'$CH_{4}$',
                          r'$C_{2}H_{n}$',
                          r'LHV',
                          r'Tar',
                          r'$Y_{Gas}$',
                          r'$Y_{Char}$'
                          ],
                         loc='upper left',
                         fontsize=plot_style.legend_fontsize_small,
                         ncol=2,
                         columnspacing=0.6,
                         borderpad=0.2,
                         labelspacing=0.3)

    ax.set_xlabel("Scaled Targets", fontsize=plot_style.labels_fontsize)
    ax.set_ylabel("Scaled Predictions", fontsize=plot_style.labels_fontsize)
    ax.tick_params(labelsize=plot_style.ticks_fontsize)

    # Add best fit line
    line = np.linspace(min(scaled_array), max(scaled_array))
    ax.plot(line, line, color='black', linewidth=2, linestyle="dashed", zorder=4)

    # Add error regions
    error_region_10 = ax.fill_between(line, line - 0.1, line + 0.1, color="blue", alpha=0.1, zorder=1,
                                      label="10% error")  # 10% error
    error_region_20 = ax.fill_between(line, line - 0.2, line + 0.2, color="blue", alpha=0.05, zorder=2,
                                      label="20% error")  # 20% error

    legend_2 = plt.legend(handles=[error_region_10, error_region_20], loc="lower right",
                          fontsize=plot_style.legend_fontsize_small)

    plt.gca().add_artist(legend_1)
    plt.gca().add_artist(legend_2)

    # Save figure if desired
    if save_fig:
        filename = model_type + "_combined_scatter" + ".png"
        storage_location = os.path.join(str(get_project_root()), "figures/EUBCE_2023_presentation")
        plt.savefig(os.path.join(storage_location, filename))

    plt.show()

    return fig, ax


def individual_feat_imp_plot(performance_summary, plot_type, plot_style=None, error_bar=True, shap_set='train',
                             save=False, save_loc='any'):
    """
    Plot various individual feature importance plots.

    Parameters
    ----------
    performance_summary: DataFrame
        Contains the performance summary of trained models.
    plot_type: str
        Defines which type of plot should be plotted (i.e. 'gini', 'perm', 'shap').
    plot_style: bool | DynaBox
        Defines the figure style (e.g. font size, figure size, etc.).
    error_bar: Bool
        Defines whether error bars should be shown for 'perm' plot (default: True).
    shap_set: str
        Defines whether train or test set should be used to display shap plots (default: 'train').
    save: bool
        Defines whether the figure should be saved (default: False).
    save_loc: str
        Defines where the model should be saved - i.e. folder indicating the model type (default: 'any').

    Returns
    -------

    """
    # TODO: Update this function if required - currently mostly just copied over from original Jupyter Notebook and
    #  only gini importance implemented.

    # Get defaults
    if plot_style is None:
        plot_style = settings.plotting.poster

    # Define common parameters
    bar_thickness = 0.8
    storage_location = "figures/EUBCE_2023_presentation"
    one_hot_encoded_predictors = np.array(['C [%daf]',
                                           'H [%daf]',
                                           'S [%daf]',
                                           'Particle size [mm]',
                                           'Ash [%db]',
                                           'Moisture [%wb]',
                                           'Temperature [°C]',
                                           'Operation (Batch/Continuous)',
                                           'ER',
                                           'Catalyst',
                                           'Scale',
                                           'Agent_air',
                                           'Agent_air + steam',
                                           'Agent_other',
                                           'Agent_oxygen',
                                           'Agent_steam',
                                           'Reactor_fixed bed',
                                           'Reactor_fluidised bed',
                                           'Reactor_other',
                                           'Bed_N/A',
                                           'Bed_alumina',
                                           'Bed_olivine',
                                           'Bed_other',
                                           'Bed_silica'])

    # Initialise Figure
    fig, ax = plt.subplots(figsize=tuple(plot_style.fig_size), dpi=plot_style.fig_dpi, tight_layout=True)

    if plot_type == 'gini':
        for count, model in enumerate(np.arange(performance_summary.loc['model'].shape[0])):
            predicted_output_name = performance_summary.columns[
                count]  # extract name of predicted output variable
            print('Gini importance of model predicting:', predicted_output_name)

            # extract importances and sorting index
            importances = performance_summary.loc['gini'][predicted_output_name]
            sorted_idx = performance_summary.loc['gini'][predicted_output_name].argsort()

            # plot importances
            plt.barh(one_hot_encoded_predictors[sorted_idx], importances[sorted_idx])
            plt.xlabel('Gini Feature Importance')
            plt.show()

            if save:
                fig.savefig(storage_location + r'\Figures\\Individual Feature Importance Graphs\\' + save_loc +
                            r'\\Gini_output_' + save_loc + '_' + str(count) + '.png')

    elif plot_type == 'perm':
        for count, model in enumerate(np.arange(performance_summary.loc['model'].shape[0])):
            predicted_output_name = performance_summary.columns[
                count]  # extract name of predicted output variable
            print('Feature permutation importance of model predicting:', predicted_output_name)

            # extract importances and sorting index
            importances = performance_summary.loc['perm_imp_mean'][predicted_output_name]
            std = performance_summary.loc['perm_imp_std'][predicted_output_name]
            sorted_idx = performance_summary.loc['perm_imp_mean'][predicted_output_name].argsort()

            # plot importances
            if error_bar == True:
                plt.barh(one_hot_encoded_predictors[sorted_idx], importances[sorted_idx], xerr=std)
            else:
                plt.barh(one_hot_encoded_predictors[sorted_idx], importances[sorted_idx])

            plt.xlabel('Permutation Feature Importance')
            plt.show()

            if save:
                fig.savefig(storage_location + r'\Figures\\Individual Feature Importance Graphs\\' + save_loc +
                            r'\\Perm_output_' + save_loc + '_' + str(count) + '.png')

    elif plot_type == 'shap':
        for count, model in enumerate(np.arange(performance_summary.loc['model'].shape[0])):
            predicted_output_name = performance_summary.columns[
                count]  # extract name of predicted output variable
            print('Shap importance of model predicting:', predicted_output_name)

            # extract importances and sorting index and plot importances
            if shap_set == 'train':
                importances = performance_summary.loc['shap_train'][predicted_output_name]

                fig = plt.figure(figsize=(12, 8))
                ax1 = fig.add_subplot(121)
                shap.summary_plot(importances, performance_summary.loc['x_train'][count], plot_type='bar',
                                  plot_size=None, show=False, max_display=24)
                ax1.set_xlabel(r'Mean SHAP values', fontsize=12)
                ax2 = fig.add_subplot(122)
                shap.summary_plot(importances, performance_summary.loc['x_train'][count], plot_size=None,
                                  show=False, max_display=24)  # note: other plot types like violin plot etc available
                ax2.set_xlabel(r'SHAP values', fontsize=12)
                plt.tight_layout()
                plt.show()

            elif shap_set == 'test':
                importances = performance_summary.loc['shap_test'][predicted_output_name]

                fig = plt.figure(figsize=(15, 10))
                ax1 = fig.add_subplot(121)
                shap.summary_plot(importances, performance_summary.loc['x_test'][count], plot_type='bar',
                                  plot_size=None, show=False, max_display=24)
                ax1.set_xlabel(r'Mean SHAP values', fontsize=12)
                ax2 = fig.add_subplot(122)
                shap.summary_plot(importances, performance_summary.loc['x_test'][count], plot_size=None,
                                  show=False, max_display=24)
                ax2.set_xlabel(r'SHAP values', fontsize=12)
                plt.tight_layout()
                plt.show()

            if save:
                fig.savefig(storage_location + r'\Figures\\Individual Feature Importance Graphs\\' + save_loc +
                            r'\Shap_output_' + save_loc + '_' + str(count) + '.png')

    else:
        print('Warning: Plottype not supported!')

    return fig


def combined_feat_imp_plot(performance_summary, model_type, plot_style=None, no_plots=1, error_bar=True,
                           legend_style="long", save=False, save_loc='any'):
    """
    Plot various  combined feature importance plots. Importances are normalised, so that each output contributes equally
     to plot.

    Parameters
    ----------
    performance_summary: DataFrame
        Contains the performance summary of trained models.
    model_type: str
        Defines which type of plot should be plotted (i.e. 'gini', 'perm', 'shap').
    plot_style: str | DynaBox
        Defines the figure style (e.g. font size, figure size, etc.).
    no_plots: Int
        Defines whether both plots should be shown or only the first one (default: 1 (i.e. only plot second figure))
    error_bar: Bool
        Defines whether error bars should be shown for 'perm' plot (default: True).
    legend_style: str
        Detailed or non-detailed legend - use "long" or "short"
    save: bool
        Defines whether the figure should be saved (default: False).
    save_loc: str
        Defines where the model should be saved - i.e. folder indicating the model type (default: 'any').

    Returns
    -------

    """

    # Get defaults
    if plot_style is None:
        plot_style = settings.plotting.poster

    # Define common parameters
    # plt.style.use('_mpl-gallery-nogrid') # use a different style
    bar_thickness = 0.8
    labels = performance_summary.loc['x_test'][0].columns
    storage_location = os.path.join(str(get_project_root()), "figures/EUBCE_2023_presentation")

    if model_type == 'gini':
        # Take sum of all importances
        imp_arrays = list()  # create list of gini values of all models
        for i in np.arange(performance_summary.loc['model'].shape[0]):
            imp_arrays.insert(i, performance_summary.loc['gini'][i])  # fill list

        # Normalise imp_arrays and calculate sums and get sorting index
        imp_arrays_norm = normalize(imp_arrays, norm="l1", axis=1)  # use "l1" so that each output contributes equally
        imp_sum = np.array(sum([sum(x) for x in zip(imp_arrays_norm)])) / performance_summary.loc['model'].shape[0]
        imp_sum_sorted_idx = imp_sum.argsort()  # to order bars in descending order

        if no_plots != 1:
            # Fig 1: Plot sum of feature importances (i.e. without showing contributions)
            fig, ax = plt.subplots()
            ax.barh(labels[imp_sum_sorted_idx], imp_sum[imp_sum_sorted_idx], height=bar_thickness)
            ax.set_xlabel('Gini Importance Scores')
            plt.tight_layout()
            plt.show()

        # Fig 2: Plot sum of feature importances with contributions
        # Initialise running total vector
        running_total_importances = np.array([0] * np.size(performance_summary.loc['gini'][1]))

        fig_size = ((plot_style.fig_size[1] * 1.2), plot_style.fig_size[0])
        fig, ax = plt.subplots(figsize=fig_size, dpi=plot_style.fig_dpi, tight_layout=True)

        for count, model in enumerate(np.arange(performance_summary.loc['model'].shape[0])):

            predicted_output_name = performance_summary.columns[count]  # extract name of predicted output variable
            importances = imp_arrays_norm[count][:]  # get normalised importances

            # Calculate running total & plot
            if count == 0:
                # Plot directly
                ax.barh(labels[imp_sum_sorted_idx], importances[imp_sum_sorted_idx], height=bar_thickness,
                        label=predicted_output_name)
            else:
                predicted_output_name_prev = performance_summary.columns[
                    count - 1]  # extract name of predicted output variable
                importances_prev = imp_arrays_norm[count - 1][:][imp_sum_sorted_idx]  # get normalised importances
                running_total_importances = running_total_importances + importances_prev  # calculate running total
                # Plot with running total as 'left'
                ax.barh(labels[imp_sum_sorted_idx], importances[imp_sum_sorted_idx], height=bar_thickness,
                        label=predicted_output_name, left=running_total_importances)

        if legend_style == "short":
            ax.legend([r'$N_{2}$',
                       r'$H_{2}$',
                       r'CO',
                       r'$CO_{2}$',
                       r'$CH_{4}$',
                       r'$C_{2}H_{n}$',
                       r'LHV',
                       r'Tar',
                       r'$Y_{Gas}$',
                       r'$Y_{Char}$'
                       ],
                      fontsize=plot_style.legend_fontsize_small,
                      borderpad=0.2,
                      labelspacing=0.3)
        elif legend_style == "long":
            ax.legend([r'$N_{2}$ [vol. % db]',
                       r'$H_{2}$ [vol. % db]',
                       r'CO [vol. % db]',
                       r'$CO_{2}$ [vol. % db]',
                       r'$CH_{4}$ [vol. % db]',
                       r'$C_{2}H_{n}$ [vol. % db]',
                       r'LHV [MJ/$Nm^{3}$]',
                       r'Tar [g/$Nm^{3}$]',
                       r'Gas Yield [$Nm^{3}$/kg wb]',
                       r'Char Yield [g/kg wb]'
                       ],
                      fontsize=plot_style.legend_fontsize_small,
                      borderpad=0.2,
                      labelspacing=0.3)
        else:
            raise ValueError("Wrong legend style.")

        ax.set_xlabel('Norm. Gini Importance', fontsize=plot_style.labels_fontsize)
        ax.tick_params(labelsize=plot_style.ticks_fontsize)
        ax.tick_params(axis="x_source", labelsize=plot_style.ticks_fontsize)
        ax.tick_params(axis="y_source", labelsize=plot_style.ticks_fontsize - 8)

        if save:
            filename = "gini_stacked" + ".png"

            fig.savefig(os.path.join(storage_location, filename))

        plt.show()

    elif model_type == 'perm':
        # Take sum of all importances
        imp_arrays = list()  # create list of permutation importance values of all models
        for i in np.arange(performance_summary.loc['model'].shape[0]):
            imp_arrays.insert(i, performance_summary.loc['perm_imp_mean'][i])  # fill list

        # Normalise imp_arrays and calculate sums and get sorting index
        imp_arrays_norm = normalize(imp_arrays, norm="l1", axis=1)  # use "l1" so that each output contributes equally
        imp_sum = np.array(sum([sum(x) for x in zip(imp_arrays_norm)])) / performance_summary.loc['model'].shape[0]
        imp_sum_sorted_idx = imp_sum.argsort()  # to order bars in descending order

        # Take sum of all std values
        imp_std_arrays = list()  # create list of permutation importance std values of all models
        for i in np.arange(performance_summary.loc['model'].shape[0]):
            imp_std_arrays.insert(i, performance_summary.loc['perm_imp_std'][i])  # fill list
        imp_std_arrays_norm = normalize(imp_arrays, norm="l1", axis=1)
        std_sum = np.array(sum([sum(x) for x in zip(imp_std_arrays_norm)])) / performance_summary.loc['model'].shape[0]

        if no_plots != 1:
            # Fig 1: Plot sum of feature importances (i.e. without showing contributions)
            fig, ax = plt.subplots()
            if error_bar == True:
                ax.barh(labels[imp_sum_sorted_idx], imp_sum[imp_sum_sorted_idx], height=bar_thickness, xerr=std_sum)
            else:
                ax.barh(labels[imp_sum_sorted_idx], imp_sum[imp_sum_sorted_idx], height=bar_thickness)
            ax.set_xlabel('Permutation Importance Scores')
            plt.tight_layout()
            plt.show()

        # Fig 2: Plot sum of feature importances with contributions
        # Initialise running total vector
        running_total_importances = np.array([0] * np.size(performance_summary.loc['perm_imp_mean'][1]))

        fig_size = ((plot_style.fig_size[1] * 1.2), plot_style.fig_size[0])
        fig, ax = plt.subplots(figsize=fig_size, dpi=plot_style.fig_dpi, tight_layout=True)

        for count, model in enumerate(np.arange(performance_summary.loc['model'].shape[0])):

            predicted_output_name = performance_summary.columns[count]  # extract name of predicted output variable
            importances = imp_arrays_norm[count][:]   # get normalised importances

            # Calculate running total & plot
            if count == 0:
                # Plot directly
                ax.barh(labels[imp_sum_sorted_idx], importances[imp_sum_sorted_idx], height=bar_thickness,
                        label=predicted_output_name)
            else:
                predicted_output_name_prev = performance_summary.columns[
                    count - 1]  # extract name of predicted output variable
                importances_prev = imp_arrays_norm[count - 1][:][imp_sum_sorted_idx]   # get normalised importances
                running_total_importances = running_total_importances + importances_prev  # calculate running total
                # Plot with running total as 'left'
                ax.barh(labels[imp_sum_sorted_idx], importances[imp_sum_sorted_idx], label=predicted_output_name,
                        height=bar_thickness, left=running_total_importances)

        if legend_style == "short":
            ax.legend([r'$N_{2}$',
                       r'$H_{2}$',
                       r'CO',
                       r'$CO_{2}$',
                       r'$CH_{4}$',
                       r'$C_{2}H_{n}$',
                       r'LHV',
                       r'Tar',
                       r'$Y_{Gas}$',
                       r'$Y_{Char}$'
                       ],
                      fontsize=plot_style.legend_fontsize_small,
                      borderpad=0.2,
                      labelspacing=0.3)
        elif legend_style == "long":
            ax.legend([r'$N_{2}$ [vol. % db]',
                       r'$H_{2}$ [vol. % db]',
                       r'CO [vol. % db]',
                       r'$CO_{2}$ [vol. % db]',
                       r'$CH_{4}$ [vol. % db]',
                       r'$C_{2}H_{n}$ [vol. % db]',
                       r'LHV [MJ/$Nm^{3}$]',
                       r'Tar [g/$Nm^{3}$]',
                       r'Gas Yield [$Nm^{3}$/kg wb]',
                       r'Char Yield [g/kg wb]'
                       ],
                      fontsize=plot_style.legend_fontsize_small,
                      borderpad=0.2,
                      labelspacing=0.3)
        else:
            raise ValueError("Wrong legend style.")

        ax.set_xlabel('Norm. Perm. Imp. Scores', fontsize=plot_style.labels_fontsize)
        ax.tick_params(labelsize=plot_style.ticks_fontsize)
        ax.tick_params(axis="x_source", labelsize=plot_style.ticks_fontsize)
        ax.tick_params(axis="y_source", labelsize=plot_style.ticks_fontsize - 8)

        if save:
            filename = "permutation_stacked" + ".png"

            fig.savefig(os.path.join(storage_location, filename))

        plt.show()


    elif model_type == 'shap':
        # First turn shap arrays in dataframe into required format (same format as gini and permutation feature importance arrays)
        shap_compressed = []  # initialise array to hold values
        for count, model in enumerate(
                np.arange(performance_summary.loc['model'].shape[0])):  # iterate through different models
            predicted_output_name = performance_summary.columns[
                count]  # extract name of predicted output variable

            matrix = performance_summary.loc['shap_test'][predicted_output_name]  # extract importance matrix

            for column_no in (
                    np.arange(np.shape(performance_summary.loc['shap_test'][1])[1])):  # iterate through columns
                column = np.abs(matrix[:, column_no])  # extract absolute values of 1 column at a time
                column_mean = sum(column) / (
                    np.shape(performance_summary.loc['shap_test'][1])[0])  # calulcate average across all rows
                shap_compressed.append(column_mean)  # store in array

            performance_summary.loc['shap_compressed_test'][predicted_output_name] = np.array(
                shap_compressed)  # store compressed array in dataframe
            shap_compressed = []  # reset storing array

        # Take sum of all importances
        imp_arrays = list()  # create list of shap values of all models
        for i in np.arange(performance_summary.loc['model'].shape[0]):
            imp_arrays.insert(i, performance_summary.loc['shap_compressed_test'][i])  # fill list

        # Normalise imp_arrays and calculate sums and get sorting index
        imp_arrays_norm = normalize(imp_arrays, norm="l1", axis=1)  # use "l1" so that each output contributes equally
        imp_sum = np.array(sum([sum(x) for x in zip(imp_arrays_norm)])) / performance_summary.loc['model'].shape[0]
        imp_sum_sorted_idx = imp_sum.argsort()  # to order bars in descending order

        if no_plots != 1:
            # Fig 1: Plot sum of feature importances (i.e. without showing contributions)
            fig, ax = plt.subplots()
            ax.barh(labels[imp_sum_sorted_idx], imp_sum[imp_sum_sorted_idx], height=bar_thickness)
            ax.set_xlabel('Absolute Shap Importance Scores')
            plt.tight_layout()
            plt.show()

        # Fig 2: Plot sum of feature importances with contributions
        # Initialise running total vector
        running_total_importances = np.array([0] * np.size(performance_summary.loc['shap_compressed_test'][1]))

        fig_size = ((plot_style.fig_size[1] * 1.2), plot_style.fig_size[0])
        fig, ax = plt.subplots(figsize=fig_size, dpi=plot_style.fig_dpi, tight_layout=True)

        for count, model in enumerate(np.arange(performance_summary.loc['model'].shape[0])):
            predicted_output_name = performance_summary.columns[count]  # extract name of predicted output variable
            importances = imp_arrays_norm[count][:]  # get normalised importances

            # Calculate running total & plot
            if count == 0:
                # Plot directly
                ax.barh(labels[imp_sum_sorted_idx], importances[imp_sum_sorted_idx], height=bar_thickness,
                        label=predicted_output_name)
            else:
                predicted_output_name_prev = performance_summary.columns[
                    count - 1]  # extract name of predicted output variable
                importances_prev = imp_arrays_norm[count - 1][:][imp_sum_sorted_idx]  # get normalised importances
                running_total_importances = running_total_importances + importances_prev  # calculate running total
                # Plot with running total as 'left'
                ax.barh(labels[imp_sum_sorted_idx], importances[imp_sum_sorted_idx], label=predicted_output_name,
                        height=bar_thickness, left=running_total_importances)

        if legend_style == "short":
            ax.legend([r'$N_{2}$',
                       r'$H_{2}$',
                       r'CO',
                       r'$CO_{2}$',
                       r'$CH_{4}$',
                       r'$C_{2}H_{n}$',
                       r'LHV',
                       r'Tar',
                       r'$Y_{Gas}$',
                       r'$Y_{Char}$'
                       ],
                      fontsize=plot_style.legend_fontsize_small,
                      borderpad=0.2,
                      labelspacing=0.3)
        elif legend_style == "long":
            ax.legend([r'$N_{2}$ [vol. % db]',
                       r'$H_{2}$ [vol. % db]',
                       r'CO [vol. % db]',
                       r'$CO_{2}$ [vol. % db]',
                       r'$CH_{4}$ [vol. % db]',
                       r'$C_{2}H_{n}$ [vol. % db]',
                       r'LHV [MJ/$Nm^{3}$]',
                       r'Tar [g/$Nm^{3}$]',
                       r'Gas Yield [$Nm^{3}$/kg wb]',
                       r'Char Yield [g/kg wb]'
                       ],
                      fontsize=plot_style.legend_fontsize_small,
                      borderpad=0.2,
                      labelspacing=0.3)
        else:
            raise ValueError("Wrong legend style.")

        ax.set_xlabel('Norm. Shap Importance', fontsize=plot_style.labels_fontsize)
        ax.tick_params(labelsize=plot_style.ticks_fontsize)
        ax.tick_params(axis="x_source", labelsize=plot_style.ticks_fontsize)
        ax.tick_params(axis="y_source", labelsize=plot_style.ticks_fontsize - 8)

        if save:
            filename = "shap_stacked" + ".png"

            fig.savefig(os.path.join(storage_location, filename))

        plt.show()

    else:
        print('Warning: Plottype not supported!')

    return fig, ax


def plot_SHAP_local_prediction(test_df, target_name="Gas yield [Nm3/kg wb]", plot_style=None, save=False,
                               save_type="any"):
    """

    Parameters
    ----------
    test_df: DataFrame
        Contains data for which predictions are to be made on.
    target_name: str
        Defines the target variable we are interested in (default: 'Gas yield [Nm3/kg wb]').

    plot_style: None | DynaBox

    save: bool
         Defines whether the figure should be saved (default: False).
    save_type: str
        Defines what type of data is used for model - used for saving (default: 'any').

    Returns
    -------

    """
    # Get defaults
    if plot_style is None:
        plot_style = settings.plotting.poster

    plt.rcParams.update({'font.size': 20})

    # Load optimised GBR model for chosen output
    GBR_model_optimised = pickle.loads(load_GBR_performance_summary_df().loc['model'][target_name])
    shap.initjs()

    # Create SHAP explainer and get shap values
    GBR_shap_explainer = shap.TreeExplainer(GBR_model_optimised)

    for row in np.arange(test_df.index.shape[0]):
        index_name = np.array(test_df.index)[row]
        print('Test data:', index_name)
        data_samples = pd.DataFrame([test_df.loc[index_name]])

        # Make prediction for new data
        GBR_prediction = GBR_model_optimised.predict(data_samples)
        print('Predicted', target_name, ': %.3f' % GBR_prediction)

        GBR_prediction_shap_values = GBR_shap_explainer.shap_values(data_samples)

        # Plot results:
        if save:
            filename = "individual_shap_explanation_" + save_type + "_" + index_name + ".png"
            storage_location = os.path.join(str(get_project_root()), "figures/EUBCE_2023_presentation")

            shap.force_plot(GBR_shap_explainer.expected_value, GBR_prediction_shap_values,
                            data_samples, matplotlib=True, figsize=(18, 4),
                            show=False)
            plt.tight_layout()
            plt.savefig(os.path.join(storage_location, filename), dpi=plot_style.fig_dpi, bbox_inches='tight')
            plt.show()
        else:
            shap.force_plot(GBR_shap_explainer.expected_value, GBR_prediction_shap_values, data_samples,
                            matplotlib=True, figsize=(18, 4), show=False)

        plt.show()
