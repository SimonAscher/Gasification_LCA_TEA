import datetime
import math

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from config import settings
from dataclasses import dataclass
from typing import Type
from human_id import generate_id
from configs.process_objects import Process
from matplotlib.backends.backend_pdf import PdfPages
from functions.LCA import electricity_GWP, thermal_energy_GWP
from processes.general import oxygen_rng_elect_req, steam_rng_heat_req


@dataclass
class Results:
    name: str = None
    processes: tuple[Type[Process]] = ()
    # TODO: Update type hint, so it properly shows children of _Requirement class.
    information: str = None

    # Define defaults which are to be populated later
    GWP_total: list[float] = None
    GWP_mean: float = None

    def __post_init__(self):
        self.ID: str = generate_id()
        self.date_time: str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

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
        # Calculate totals for each Monte Carlo instance
        GWP_totals = []
        for process in self.processes:
            GWP_totals.append(np.array(process.GWP_total).flatten())
        GWP_totals = np.array(GWP_totals)
        self.GWP_total = list(np.sum(GWP_totals, axis=0))  # sum elementwise

        # Calculate overall sum
        self.GWP_mean = float(np.mean(self.GWP_total))

    def calculate_electricity_heat_output(self):
        electricity_arrays = []
        heat_arrays = []

        def extract_heat_electricity_from_requirement(requirement_obj, electricity_storage_array, heat_storage_array):
            for requirement_instance in requirement_obj.electricity:  # electricity requirements
                if requirement_instance.generated:
                    values = [-x for x in requirement_instance.values]
                    electricity_storage_array.append(values)
                else:
                    electricity_storage_array.append(requirement_instance.values)

            for requirement_instance in requirement_obj.oxygen:  # oxygen requirements - also result in electricity
                ele_oxygen = []
                for oxygen_req_value in requirement_instance.values:
                    ele_oxygen.append(electricity_GWP(amount=oxygen_rng_elect_req(mass_oxygen=oxygen_req_value)))
                electricity_storage_array.append(ele_oxygen)

            for requirement_instance in requirement_obj.heat:  # heat requirements
                if requirement_instance.generated:
                    values = [-x for x in requirement_instance.values]
                    heat_storage_array.append(values)
                else:
                    heat_storage_array.append(requirement_instance.values)

            for requirement_instance in requirement_obj.steam:  # steam requirements - also result in heat
                heat_steam = []
                for steam_req_value in requirement_instance.values:
                    heat_steam.append(thermal_energy_GWP(amount=steam_rng_heat_req(mass_steam=steam_req_value)))
                heat_storage_array.append(heat_steam)

            return electricity_storage_array, heat_storage_array

        for process in self.processes:  # iterate through processes
            for requirement in process.requirements:  # iterate through requirements of each process.
                electricity_arrays, heat_arrays = extract_heat_electricity_from_requirement(requirement,
                                                                                            electricity_arrays,
                                                                                            heat_arrays)
            for subprocess in process.subprocesses:
                for sub_requirement in subprocess.requirements:
                    electricity_arrays, heat_arrays = extract_heat_electricity_from_requirement(sub_requirement,
                                                                                                electricity_arrays,
                                                                                                heat_arrays)

                    for sub_sub_requirement in subprocess.subprocesses:
                        electricity_arrays, heat_arrays = extract_heat_electricity_from_requirement(sub_sub_requirement,
                                                                                                    electricity_arrays,
                                                                                                    heat_arrays)

        # Calculate net output
        electricity_output_distribution = list(np.sum(np.array(electricity_arrays), axis=0) * -1)
        heat_output_distribution = list(np.sum(np.array(heat_arrays), axis=0) * -1)

        self.electricity_output = {"Mean:": np.mean(electricity_output_distribution),
                                   "Distribution:": electricity_output_distribution}
        self.heat_output = {"Mean:": np.mean(heat_output_distribution),
                            "Distribution:": heat_output_distribution}

    def calculate_total_TEA(self):
        pass

    def plot_global_GWP(self, bins=20):
        """

        Parameters
        ----------
        bins: int
            Number of bins for histogram.

        Returns
        -------

        """
        sns.set_theme()
        fig, ax = plt.subplots()
        ax.hist(self.GWP_total, bins=bins)

        # Set title and labels
        ax.set_xlabel(settings.labels.LCA_output_plotting_string)
        ax.set_ylabel("Monte Carlo Iterations")

        # Display plot
        plt.tight_layout()
        plt.show()

        return fig, ax

    def plot_average_GWP_byprocess(self, legend_loc="plot", short_labels=True,
                                   save=(False, "placeholder_save_location_str")):
        """


        Notes: Generally legend_loc="plot" and short_labels=True OR legend_loc="box" and short_labels=False
        produces the best results.

        Parameters
        ----------
        legend_loc: str
            Determine whether subprocess labels should be placed on plot ("plot") or in legend box ("box").
        short_labels: bool
            Determines whether shortened labels should be used (True) or not (False).
        save

        Returns
        -------

        """
        # Setup general variables
        sns.set_theme()
        bar_width = 0.5

        # Get process names and shorthands for names
        names = []
        short_names = []
        for process in self.processes:
            names.append(process.name)
            short_names.append(process.short_label)

        x_array = names
        x_array.append("Total")  # Last element on axis

        # Initialise figure
        fig, ax = plt.subplots()

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
                y_array = np.zeros(len(x_array))  # Initialise y-array
                y_array[process_count] = subprocess_GWP_mean  # Update y-array with GWP in appropriate position

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
                                 fontsize=12,
                                 horizontalalignment='center'
                                 )
        # Add final bar showing total/overall GWP
        y_array = np.zeros(len(x_array))  # Initialise y-array
        y_array[-1] = self.GWP_mean  # Update y-array with GWP
        ax.bar(x_array, y_array, bar_width, label="Total")

        # Set labels
        ax.set_ylabel(settings.labels.LCA_output_plotting_string)
        plt.xticks(rotation=45)

        # Display legend
        if legend_loc == "box":
            ax.legend()

        # Display plot
        plt.tight_layout()
        plt.show()

        return fig, ax

    def plot_global_GWP_byprocess(self, bins=50, short_labels=False, show_total=True):
        """
        Plots Monte Carlo distribution of each process' GWP.

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
        marker_threshold = settings.background.iterations_MC * 0.01  # threshold below which markers are not displayed

        # Plot histograms and total
        sns.set_theme()  # Use seaborn style
        fig, ax = plt.subplots()

        # Plot histograms
        ax.hist(GWP_exc_total, bins=bin_vector, histtype='bar', stacked=True, label=process_names[0:-1])

        if show_total:  # Plot total whilst excluding zeros or very low values for plotting
            ax.scatter(marker_x[marker_y > marker_threshold], marker_y[marker_y > marker_threshold],
                       label=process_names[-1],
                       marker="x", color="black", alpha=0.8)

        # Set legend and labels
        ax.legend()
        ax.set_xlabel(settings.labels.LCA_output_plotting_string)
        ax.set_ylabel("Monte Carlo Iterations")

        # Display plot
        plt.tight_layout()
        plt.show()

        return fig, ax

    def plot_TEA(self):
        pass

    def plot_sankey_diagram(self):
        pass

    def plot_results(self, show_GWP=True, show_TEA=True):
        if show_GWP:
            self.plot_global_GWP()
            self.plot_global_GWP_byprocess()
            self.plot_average_GWP_byprocess()
        if show_TEA:
            self.plot_TEA()

    def save_report(self, storage_path):
        """
        Saves all figure as a pdf report.

        Parameters
        ----------
        storage_path: str
            Raw string indicating where the file should be stored.

        Returns
        -------

        """
        fig1, ax1 = self.plot_global_GWP()
        fig2, ax2 = self.plot_global_GWP_byprocess()
        fig3, ax3 = self.plot_average_GWP_byprocess()
        # fig4, ax4 = self.plot_TEA()

        filename = r"\report_" + self.ID + ".pdf"
        full_path = storage_path + filename
        file = PdfPages(full_path)
        file.savefig(fig1)
        file.savefig(fig2)
        file.savefig(fig3)
        # file.savefig(fig4)
        file.close()
