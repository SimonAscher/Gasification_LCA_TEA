import datetime
import math
import os
import pathlib
import shutil

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from config import settings
from dynaconf.utils.boxing import DynaBox
from dataclasses import dataclass
from typing import Type
from human_id import generate_id
from objects.process_objects import Process
from matplotlib.backends.backend_pdf import PdfPages
from functions.LCA import electricity_GWP, thermal_energy_GWP
from processes.general import oxygen_rng_elect_req, steam_rng_heat_req


@dataclass
class Results:
    """
    Combines a number of processes and calculates their life cycle assessment (LCA) and
    techno-economic analysis (TEA) results.

    Attributes
    ----------
    name: str
        Name given to the results.
    processes: tuple[Type[Process]]
        Tuple of process objects making up the results.
    information: str
        Additional information can be added here.
    plot_style: str | DynaBox
        Style to be used for plotting - str loads predefined style from settings (e.g. "digital" or "poster").
        Alternatively DynaBox object can be given directly.
    GWP_total: list[float]
        GWP Monte Carlo results - populated later.
    GWP_mean: float
        Average GWP - populated later.
    electricity_results: dict
        Electricity generation and use results - populated later.
    heat_results: dict
        Heat/thermal energy generation and use results - populated later.
    figures: dict
        Dictionary of figures illustrating environmental and economic results.

    ID: str
        Unique identifier given to this set of results. Created when object is instantiated. Automatically added.
    date_time: str
        Date and time when results were instantiated. Automatically added.

    Methods
    -------
    add_process(process):
        Allows for the addition of a process after the results objects has been initialised.

    calculate_total_GWP():
        Calculates the overall global warming potential (GWP) of the system.

    """
    # TODO: Add other methods to docstring.
    name: str = None
    processes: tuple[Type[Process]] = ()
    # TODO: Update type hint, so it properly shows children of _Requirement class.
    information: str = None
    plot_style: str | DynaBox = "digital"  # default style for plots

    # Define defaults which are to be populated later
    GWP_total: list[float] = None
    GWP_mean: float = None
    electricity_results: dict = None
    heat_results: dict = None
    figures: dict = None

    def __post_init__(self):
        self.ID: str = generate_id()
        self.date_time: str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if type(self.plot_style) != DynaBox:
            self.plot_style = settings.plotting[self.plot_style]  # update plot style

    def add_process(self, process):
        """
        Allows for the addition of a process after the results objects has been initialised.

        Parameters
        ----------
        process: Process
            Process object which is to be added to results.
        """
        self.processes += (process, )

    def calculate_total_GWP(self):
        """
        Calculates the overall global warming potential (GWP) of the system.
        """
        # Calculate totals for each Monte Carlo instance
        GWP_totals = []
        for process in self.processes:
            GWP_totals.append(np.array(process.GWP_total).flatten())
        GWP_totals = np.array(GWP_totals)
        self.GWP_total = list(np.sum(GWP_totals, axis=0))  # sum elementwise

        # Calculate overall sum
        self.GWP_mean = float(np.mean(self.GWP_total))


    def calculate_total_TEA(self):
        pass

    def calculate_electricity_heat_output(self):
        """
        Calculates the overall energy outputs in the form of electricity and heat of the system.
        """
        # Storage lists
        electricity = []
        electricity_names = []
        heat = []
        heat_names = []

        # Define helper function
        def extract_heat_electricity_from_requirement(requirement_obj, electricity_storage_array, heat_storage_array,
                                                      electricity_names_array, heat_names_array):
            # electricity requirements
            for requirement_instance in requirement_obj.electricity:
                electricity_names_array.append(requirement_instance.name)
                if requirement_instance.generated:
                    values = [-x for x in requirement_instance.values]
                    electricity_storage_array.append(values)
                else:
                    electricity_storage_array.append(requirement_instance.values)

            # oxygen requirements - also result in electricity
            for requirement_instance in requirement_obj.oxygen:
                ele_oxygen = []
                electricity_names_array.append(requirement_instance.name)
                for oxygen_req_value in requirement_instance.values:
                    ele_oxygen.append(electricity_GWP(amount=oxygen_rng_elect_req(mass_oxygen=oxygen_req_value)))
                electricity_storage_array.append(ele_oxygen)

            # heat requirements
            for requirement_instance in requirement_obj.heat:
                heat_names_array.append(requirement_instance.name)
                if requirement_instance.generated:
                    values = [-x for x in requirement_instance.values]
                    heat_storage_array.append(values)
                else:
                    heat_storage_array.append(requirement_instance.values)

            # steam requirements - also result in heat
            for requirement_instance in requirement_obj.steam:
                heat_steam = []
                heat_names_array.append(requirement_instance.name)
                for steam_req_value in requirement_instance.values:
                    heat_steam.append(thermal_energy_GWP(amount=steam_rng_heat_req(mass_steam=steam_req_value)))
                heat_storage_array.append(heat_steam)

            return electricity_storage_array, heat_storage_array, electricity_names_array, heat_names_array

        # Employ helper function up to the third layer of subprocesses
        for process in self.processes:  # iterate through processes
            for requirement in process.requirements:  # iterate through requirements of each process.
                electricity, heat, electricity_names, heat_names = \
                    extract_heat_electricity_from_requirement(requirement, electricity, heat,
                                                              electricity_names, heat_names)
            for subprocess in process.subprocesses:
                for sub_requirement in subprocess.requirements:
                    electricity, heat, electricity_names, heat_names = \
                        extract_heat_electricity_from_requirement(sub_requirement, electricity, heat,
                                                                  electricity_names, heat_names)

                    for sub_sub_requirement in subprocess.subprocesses:
                        electricity, heat, electricity_names, heat_names = \
                            extract_heat_electricity_from_requirement(sub_sub_requirement, electricity, heat,
                                                                      electricity_names, heat_names)

        # Calculate net output in different forms
        electricity_components = np.array(electricity) * -1
        heat_components = np.array(heat) * -1
        electricity_output_distribution = list(np.sum(electricity_components, axis=0))
        heat_output_distribution = list(np.sum(heat_components, axis=0))

        electricity_output = {"Total mean": np.mean(electricity_output_distribution),
                              "Total MC distribution": electricity_output_distribution,
                              "Component distributions": electricity_components,
                              "Component means": np.mean(electricity_components, axis=1),
                              "Component names": electricity_names}

        heat_output = {"Total mean": np.mean(heat_output_distribution),
                       "Total MC distribution": heat_output_distribution,
                       "Component distributions": heat_components,
                       "Component means": np.mean(heat_components, axis=1),
                       "Component names": heat_names}

        # Store results in object
        self.electricity_results = electricity_output
        self.heat_results = heat_output

        return electricity_output, heat_output

    def update_plot_style(self, style=None, style_box=None):
        """
        Updates the plot style to be used - which effects figure size, font size, dpi, etc.
        Use either style or style_box.
        Parameters
        ----------
        style: str
            Style identifier corresponding to style defined in settings.plotting.
        style_box: DynaBox
            User defined box with relevant plotting parameters.
        """
        if style is not None:
            self.plot_style = settings.plotting[style]
        elif style_box is not None:
            self.plot_style = style_box
        else:
            raise ValueError("Either use default style via 'style' parameter or supply style_box. Do not use both.")

    def plot_energy_global(self, bins=10):
        """
        Create plot to illustrate the global energy generation performance of the system.

        Parameters
        ----------
        bins: int
            Number of bins to be used for plot.

        Returns
        -------

        """
        # Get required data
        electricity_data, heat_data = self.electricity_results, self.heat_results

        sns.set_theme()
        fig, ax = plt.subplots(figsize=tuple(self.plot_style.fig_size), dpi=self.plot_style.fig_dpi)
        ax.hist(electricity_data["Total MC distribution"], bins, alpha=0.8)
        ax.hist(heat_data["Total MC distribution"], bins, alpha=0.8)

        # Set title and labels
        ax.legend(["Electricity", "Heat"], fontsize=self.plot_style.legend_fontsize_large,
                  loc=self.plot_style.legend_location)
        ax.set_xlabel(r"Output Energy [$kWh\ FU^{-1}$]", fontsize=self.plot_style.labels_fontsize)
        ax.set_ylabel("Monte Carlo Iterations", fontsize=self.plot_style.labels_fontsize)
        ax.tick_params(labelsize=self.plot_style.ticks_fontsize)
        plt.tight_layout()
        plt.show()
        plt.close(fig)

        return fig, ax

    def _plot_energy_byprocess(self, energy_data, bins=40, display_total=True):
        """
        Helper function to plot electricity and heat generation/consumption results by process.

        Parameters
        ----------
        bins: int
            Number of bins to be used for plot.
        display_total: bool
            Show total production/consumption.

        Returns
        -------

        """
        # Extract required values
        process_names = energy_data["Component names"]
        GWP_matrix = list(energy_data["Component distributions"])

        # Add total and prepare plotting format
        process_names.append("Total")
        GWP_matrix.append(energy_data["Total MC distribution"])
        GWP_matrix = np.transpose(np.array(GWP_matrix))  # convert to right format
        GWP_exc_total = GWP_matrix[:, 0:-1]  # get list without the total
        GWP_total = GWP_matrix[:, -1]  # get list of total GWP

        # Turn bin number into a bin vector which can be used to plot histograms and total
        bin_width = round((np.max(GWP_matrix) - np.min(GWP_matrix)) / bins)
        min_value = math.floor(np.min(GWP_matrix))
        max_value = math.ceil(np.max(GWP_matrix))
        bin_vector = range(min_value, max_value + bin_width, bin_width)

        # Get total marker coordinates
        marker_x = np.array(plt.hist(GWP_total, bins=bin_vector, alpha=0, histtype='bar')[1][0:-1])
        marker_y = np.array(plt.hist(GWP_total, bins=bin_vector, alpha=0, histtype='bar')[0])
        plt.clf()  # to prevent interference with actual plot
        marker_threshold = settings.user_inputs.general.MC_iterations * 0.01  # threshold below which markers are not displayed

        # Plot histograms and total
        sns.set_theme()  # Use seaborn style
        fig, ax = plt.subplots(figsize=tuple(self.plot_style.fig_size), dpi=self.plot_style.fig_dpi)
        # Plot histograms
        ax.hist(GWP_exc_total, bins=bin_vector, histtype='bar', stacked=True, label=process_names[0:-1])

        if display_total:  # Plot total whilst excluding zeros or very low values for plotting
            ax.scatter(marker_x[marker_y > marker_threshold], marker_y[marker_y > marker_threshold],
                       label=process_names[-1],
                       marker="x_source",
                       s=self.plot_style.marker_size,
                       color="black",
                       alpha=0.8)

        # Set legend and labels
        ax.legend(fontsize=self.plot_style.legend_fontsize_small, loc=self.plot_style.legend_location)
        ax.set_xlabel(r"Output Energy [$kWh\ FU^{-1}$]", fontsize=self.plot_style.labels_fontsize)
        ax.set_ylabel("Monte Carlo Iterations", fontsize=self.plot_style.labels_fontsize)
        ax.tick_params(labelsize=self.plot_style.ticks_fontsize)

        # Display plot
        plt.tight_layout()
        plt.show()
        plt.close(fig)

        return fig, ax

    def plot_energy_electricity(self, bins=None, show_total=True):
        """
        Plot electricity generation/consumption of system.

        Parameters
        ----------
        bins: int
            Number of bins to be used for plot.
        show_total: bool
            Show total production/consumption.

        Returns
        -------

        """
        # Get defaults
        if bins is None:
            bins = 40

        data = self.electricity_results

        fig, ax = self._plot_energy_byprocess(energy_data=data, bins=bins, display_total=show_total)

        return fig, ax

    def plot_energy_heat(self, bins=None, show_total=True):
        """
        Plot heat generation/consumption of system.

        Parameters
        ----------
        bins: int
            Number of bins to be used for plot.
        show_total: bool
            Show total production/consumption.

        Returns
        -------
        matplotlib.pyplot.figure, matplotlib.pyplot.axes
        """
        # Get defaults
        if bins is None:
            bins = 40

        data = self.heat_results

        fig, ax = self._plot_energy_byprocess(energy_data=data, bins=bins, display_total=show_total)

        return fig, ax

    def plot_global_GWP(self, bins=20):
        """
        Creates plot of the systems overall global warming potential (GWP).
        Parameters
        ----------
        bins: int
            Number of bins for histogram.

        Returns
        -------
        matplotlib.pyplot.figure, matplotlib.pyplot.axes
            Resulting matplotlib figure and axes object.

        """
        sns.set_theme()
        fig, ax = plt.subplots(figsize=tuple(self.plot_style.fig_size), dpi=self.plot_style.fig_dpi)
        ax.hist(self.GWP_total, bins=bins)

        # Set title and labels
        ax.set_xlabel("GWP " + settings.labels.LCA_output_plotting_string, fontsize=self.plot_style.labels_fontsize)
        ax.set_ylabel("Monte Carlo Iterations", fontsize=self.plot_style.labels_fontsize)
        ax.tick_params(labelsize=self.plot_style.ticks_fontsize)

        # Display plot
        plt.tight_layout()
        plt.show()
        plt.close(fig)

        return fig, ax

    def plot_average_GWP_byprocess(self, legend_loc="plot", short_labels=True):
        """
        Creates plot of the systems average global warming potential (GWP) shown for each process.
        Note: Generally legend_loc="plot" and short_labels=True OR legend_loc="box" and short_labels=False
        produces the best results.

        Parameters
        ----------
        legend_loc: str
            Determine whether subprocess labels should be placed on plot ("plot") or in legend box ("box").
        short_labels: bool
            Determines whether shortened labels should be used (True) or not (False).

        Returns
        -------
        matplotlib.pyplot.figure, matplotlib.pyplot.axes
            Resulting matplotlib figure and axes object.
        """
        # Setup general variables
        sns.set_theme()
        bar_width = 0.5

        # Get process names and shorthands for names
        if short_labels:
            short_names = []
            for process in self.processes:
                short_names.append(process.short_label)
            x_array = short_names
        else:
            names = []
            for process in self.processes:
                names.append(process.name)
            x_array = names
        x_array.append("Total")  # Last element on axis

        # Initialise figure
        # fig_size = (self.plot_style.fig_size[0], 0.8 * self.plot_style.fig_size[0])  # to allow for more labels space
        fig_size = tuple(self.plot_style.fig_size)
        fig, ax = plt.subplots(figsize=fig_size, dpi=self.plot_style.fig_dpi)

        # Plotting logic
        for process_count, process in enumerate(self.processes):
            # Get subprocess names
            subprocess_names = []
            subprocess_short_labels = []
            GWP_totals = []

            for GWP_result in process.GWP_results:
                subprocess_names.append(GWP_result.name)
                subprocess_short_labels.append(GWP_result.short_label)
                GWP_totals.append(np.array(GWP_result.values))
            subprocess_GWPs = np.array(GWP_totals)

            # Get subprocess means and labels
            for subprocess_count, _ in enumerate(list(subprocess_GWPs)):
                subprocess_GWP_mean = np.mean(subprocess_GWPs[subprocess_count])  # calculate subprocess GWP mean
                subprocess_label = subprocess_names[subprocess_count][0]  # get subprocess name
                if short_labels:
                    subprocess_label = subprocess_short_labels[subprocess_count]  # get shorthand labels for plotting
                y_array = np.zeros(len(x_array))  # Initialise y_source-array
                y_array[process_count] = subprocess_GWP_mean  # Update y_source-array with GWP in appropriate position

                # Plot stacked bar graph for individual process
                if subprocess_count == 0:  # plot first subprocess
                    ax.bar(x_array, y_array, bar_width, label=subprocess_label)
                    if subprocess_GWP_mean > 0:  # positive number case
                        running_total_pos = y_array
                        running_total_neg = np.zeros(len(x_array))  # Initialise other case as zero
                    else:  # negative number case
                        running_total_neg = y_array
                        running_total_pos = np.zeros(len(x_array))  # Initialise other case as zero
                else:  # plot other subprocesses
                    if subprocess_GWP_mean > 0:  # positive number case
                        ax.bar(x_array, y_array, bar_width, bottom=running_total_pos, label=subprocess_label)
                        running_total_pos += y_array  # update running total
                    else:  # negative number case
                        ax.bar(x_array, y_array, bar_width, bottom=running_total_neg, label=subprocess_label)
                        running_total_neg += y_array  # update running total

                # Plot labels on graph
                if legend_loc == "plot":
                    if abs(y_array[
                               process_count]) > 50:  # Set threshold for minimum stack size to avoid overlapping labels
                        if subprocess_GWP_mean > 0:
                            y_position = (running_total_pos[process_count] - y_array[process_count]) \
                                         + y_array[process_count] * 0.5
                        else:
                            y_position = (running_total_neg[process_count] - y_array[process_count]) \
                                         + y_array[process_count] * 0.5

                        plt.text(x=x_array[process_count],
                                 y=y_position,
                                 s=subprocess_label,
                                 color="black",
                                 fontsize=self.plot_style.legend_fontsize_small,
                                 horizontalalignment="center"
                                 )
        # Add final bar showing total/overall GWP
        y_array = np.zeros(len(x_array))  # Initialise y_source-array
        y_array[-1] = self.GWP_mean  # Update y_source-array with GWP
        ax.bar(x_array, y_array, bar_width, label="Total")

        # Set labels
        ax.set_ylabel("GWP " + settings.labels.LCA_output_plotting_string, fontsize=self.plot_style.labels_fontsize)
        ax.tick_params(axis="x_source", labelsize=self.plot_style.labels_fontsize, rotation=45)
        ax.tick_params(axis="y_source", labelsize=self.plot_style.ticks_fontsize)

        # Display legend
        if legend_loc == "box":
            ax.legend(fontsize=self.plot_style.legend_fontsize_small)

        # Display plot
        plt.tight_layout()
        plt.show()
        plt.close(fig)

        return fig, ax

    def plot_global_GWP_byprocess(self, bins=50, short_labels=False, show_total=True):
        """
        Creates plot of the Monte Carlo distributions of each process' global warming potential (GWP).

        Parameters
        ----------
        bins: int
            Number of bins across all histograms.
        short_labels: bool
            Determines whether shortened labels should be used (True) or not (False).
        show_total: bool
            Show total GWP of process in addition to processes.
        Returns
        -------
        matplotlib.pyplot.figure, matplotlib.pyplot.axes
            Resulting matplotlib figure and axes object.
        """
        # Extract required values
        process_names = []
        process_short_names = []
        GWP_matrix = []
        for process_count, process in enumerate(self.processes):  # get Monte Carlo emissions of processes
            process_names.append(process.name)
            process_short_names.append(process.short_label)
            GWP_matrix.append(np.array(process.GWP_total).flatten())

        # Add total and prepare plotting format
        process_names.append("Total")
        process_short_names.append("Total")
        GWP_matrix.append(np.array(self.GWP_total))
        GWP_matrix = np.transpose(np.array(GWP_matrix))  # convert to right format
        GWP_exc_total = GWP_matrix[:, 0:-1]  # get list without the total
        GWP_total = GWP_matrix[:, -1]  # get list of total GWP

        if short_labels:
            process_names = process_short_names

        # Turn bin number into a bin vector which can be used to plot histograms and total
        bin_width = round((np.max(GWP_matrix) - np.min(GWP_matrix)) / bins)
        min_value = math.floor(np.min(GWP_matrix))
        max_value = math.ceil(np.max(GWP_matrix))
        bin_vector = range(min_value, max_value + bin_width, bin_width)

        # Get total marker coordinates
        marker_x = np.array(plt.hist(GWP_total, bins=bin_vector, alpha=0, histtype='bar')[1][0:-1])
        marker_y = np.array(plt.hist(GWP_total, bins=bin_vector, alpha=0, histtype='bar')[0])
        plt.clf()  # to prevent interference with actual plot
        marker_threshold = settings.user_inputs.general.MC_iterations * 0.01  # threshold below which markers are not displayed

        # Plot histograms and total
        sns.set_theme()  # Use seaborn style
        fig, ax = plt.subplots(figsize=tuple(self.plot_style.fig_size), dpi=self.plot_style.fig_dpi)

        # Plot histograms
        ax.hist(GWP_exc_total, bins=bin_vector, histtype='bar', stacked=True, label=process_names[0:-1])

        if show_total:  # Plot total whilst excluding zeros or very low values for plotting
            ax.scatter(marker_x[marker_y > marker_threshold], marker_y[marker_y > marker_threshold],
                       label=process_names[-1],
                       marker="x_source",
                       s=self.plot_style.marker_size,
                       color="black",
                       alpha=0.8)

        # Set legend and labels
        ax.legend(fontsize=self.plot_style.legend_fontsize_small)
        ax.set_xlabel("GWP " + settings.labels.LCA_output_plotting_string, fontsize=self.plot_style.labels_fontsize)
        ax.set_ylabel("Monte Carlo Iterations", fontsize=self.plot_style.labels_fontsize)
        ax.tick_params(labelsize=self.plot_style.labels_fontsize)

        # Display plot
        plt.tight_layout()
        plt.show()
        plt.close(fig)

        return fig, ax

    def plot_TEA(self):
        pass

    def plot_sankey_diagram(self):
        pass

    def plot_results(self, show_GWP=True, show_TEA=True, show_energy_generation=True):
        """
        Convenience function to generate all plots.

        Parameters
        ----------
        show_GWP: bool
            Show environmental analysis results.
        show_TEA: bool
            Show economic analysis results.
        show_energy_generation: bool
            Show energy generation results.
        """
        if show_GWP:
            self.plot_global_GWP()
            self.plot_global_GWP_byprocess()
            self.plot_average_GWP_byprocess()
        if show_TEA:
            self.plot_TEA()

        if show_energy_generation:
            self.plot_energy_global()
            self.plot_energy_electricity()
            self.plot_energy_heat()

    def store_figures(self):
        """
        Store all figures in results object.

        Returns
        -------

        """
        # Get figure objects
        fig1, _ = self.plot_global_GWP()
        fig2, _ = self.plot_global_GWP_byprocess()
        fig3, _ = self.plot_average_GWP_byprocess()
        fig4, _ = self.plot_energy_global()
        fig5, _ = self.plot_energy_electricity()
        fig6, _ = self.plot_energy_heat()

        self.figures = {"global_GWP": fig1,
                        "global_GWP_byprocess": fig2,
                        "average_GWP_byprocess": fig3,
                        "energy_global": fig4,
                        "energy_electricity": fig5,
                        "energy_heat": fig6
                        }

    def save_report(self, storage_path, save_figures=False):
        """
        Saves all figure as a pdf report.

        Parameters
        ----------
        storage_path: str
            Raw string indicating where the file should be stored.
        save_figures: bool
            If true also saves figures as separate files.

        Returns
        -------

        """
        # TODO: Update this method so it works properly with streamlit and store_figures function.
        if self.figures is None:
            self.store_figures()

        fig1 = self.figures["global_GWP"]
        fig2 = self.figures["global_GWP_byprocess"]
        fig3 = self.figures["average_GWP_byprocess"]
        fig4 = self.figures["energy_global"]
        fig5 = self.figures["energy_electricity"]
        fig6 = self.figures["energy_heat"]

        # Create results directory if it does not exist already
        results_dir = os.path.join(storage_path, self.ID)
        if not os.path.isdir(results_dir):  # Create directory if it does not exist already
            os.makedirs(results_dir)
        filename = "report_" + self.ID + ".pdf"
        report_path = os.path.join(results_dir, filename)

        # Save figures to pdf
        file = PdfPages(report_path)
        file.savefig(fig1)
        file.savefig(fig2)
        file.savefig(fig3)
        file.savefig(fig4)
        file.savefig(fig5)
        file.savefig(fig6)
        file.close()

        # TODO: Implement this method again - could just extract [user_inputs] and [sensitivity_analysis] sections from
        #  settings object.
        # # Save toml user input file with pdf report
        # try:
        #     user_inputs_path = settings.settings_module[7]  # save file selected by user
        # except:
        #     user_inputs_path = settings.settings_module[2]  # save default scenarios file
        #
        # shutil.copy(user_inputs_path, os.path.join(results_dir, pathlib.PurePath(user_inputs_path).name))

        # Save figure files to directory
        if save_figures:
            fig1.savefig(os.path.join(results_dir, "global_GWP.png"))
            fig2.savefig(os.path.join(results_dir, "global_GWP_byprocess.png"))
            fig3.savefig(os.path.join(results_dir, "average_GWP_byprocess.png"))
            fig4.savefig(os.path.join(results_dir, "energy_global.png"))
            fig5.savefig(os.path.join(results_dir, "energy_electricity.png"))
            fig6.savefig(os.path.join(results_dir, "energy_heat.png"))
