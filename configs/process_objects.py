import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from config import settings
from dataclasses import dataclass, InitVar
from typing import Type
from configs.requirement_objects import _Requirement, Requirements
from configs.requirement_objects import Heat, Electricity, Steam, Oxygen, FossilGWP, BiogenicGWP
from functions.LCA import electricity_GWP, thermal_energy_GWP
from processes.general import oxygen_rng_elect_req, steam_rng_heat_req


# Prerequisite and utility functions and objects
@dataclass
class GlobalWarmingPotential:
    """
    Global Warming Potential (GWP) of a process.

    Attributes
    ----------
    requirement : InitVar[Type[_Requirement]]
        A "_Requirement" child object which is to be converted to its equivalent GWP.
    """
    # TODO: Update type hint, so it properly shows children of _Requirement class.

    # Update defaults
    requirement: InitVar[Type[_Requirement]]

    def __post_init__(self, requirement):
        # Take values from requirement object
        self.values = []
        self.name = requirement.name
        self.short_label = requirement.short_label
        self.description = requirement.description
        self.source = requirement.source
        self.units = "kg CO2eq./FU"  # Update units
        self.requirement_type = str(type(requirement))  # to remember where the GWP is coming from

        # Calculate GWP and store as object attribute
        if isinstance(requirement, Electricity):
            for value in requirement.values:
                self.values.append(electricity_GWP(amount=value, source=requirement.source, units=requirement.units))
            if requirement.generated:  # i.e. leading to displacement of energy
                self.values = list(np.array(self.values) * -1)

        elif isinstance(requirement, Heat):
            for value in requirement.values:
                self.values.append(thermal_energy_GWP(amount=value, source=requirement.source, units=requirement.units))
            if requirement.generated:  # i.e. leading to displacement of energy
                self.values = list(np.array(self.values) * -1)

        elif isinstance(requirement, FossilGWP):
            self.values = requirement.values

        elif isinstance(requirement, BiogenicGWP):
            self.values = list(np.array(requirement.values) * requirement.biogenic_fraction)

        elif isinstance(requirement, Oxygen):
            for value in requirement.values:
                self.values.append(electricity_GWP(amount=oxygen_rng_elect_req(mass_oxygen=value)))
                # i.e. effectively electricity requirement

        elif isinstance(requirement, Steam):
            for value in requirement.values:
                self.values.append(thermal_energy_GWP(amount=steam_rng_heat_req(mass_steam=value)))
                # i.e. effectively heat requirement

        else:
            raise ValueError("Wrong requirement object supplied. Ensure supported type is used.")

        self.mean = np.mean(self.values)


def process_requirements_to_GWP(requirements):
    """
    Convert a process' requirements to their corresponding Global Warming Potential (GWP).

    Parameters
    ----------
    requirements: tuple[Requirements]
        Requirements attribute of "Process" object.

    Returns
    -------
    tuple[GlobalWarmingPotential]
        Global warming potentials resulting from process requirements.
    """

    GWP_results = ()
    for requirement_no in range(len(requirements)):  # iterate through requirements objects
        for fossil_GWP_requirements in requirements[requirement_no].fossil_GWP:
            GWP_results += (GlobalWarmingPotential(fossil_GWP_requirements),)
        for biogenic_GWP_requirements in requirements[requirement_no].biogenic_GWP:
            GWP_results += (GlobalWarmingPotential(biogenic_GWP_requirements),)
        for electricity_requirements in requirements[requirement_no].electricity:
            GWP_results += (GlobalWarmingPotential(electricity_requirements),)
        for heat_requirements in requirements[requirement_no].heat:
            GWP_results += (GlobalWarmingPotential(heat_requirements),)
        for steam_requirements in requirements[requirement_no].steam:
            GWP_results += (GlobalWarmingPotential(steam_requirements),)
        for oxygen_requirements in requirements[requirement_no].oxygen:
            GWP_results += (GlobalWarmingPotential(oxygen_requirements),)

    return GWP_results


# Dataclass to store process requirements
@dataclass
class Process:
    """
    Process instance. Contains all process requirements and information.

    Attributes
    ----------
    name : str
        The name of the process.
    short_label : str
        A shorthand notation of the process - used for plotting etc.
    information : str
        Additional information can be added here.
    subprocesses : tuple[Type["Process"]]
        Subprocesses of the process.
    requirements: tuple[Requirements]
        Requirements of this process
    instantiate_with_default_reqs: bool
        Determines whether the process should fetch its default requirements and calculate its GWP and TEA results from
        that.
    Methods
    -------
    add_subprocess(subprocess)
    """

    # General parameters
    name: str
    short_label: str = None
    information: str = None
    subprocesses: tuple[Type["Process"]] = ()  # Wrap name in string to forward declare
    requirements: tuple[Requirements] = ()

    # InitVars
    instantiate_with_default_reqs: bool = True

    # GWP results
    GWP_results: tuple[GlobalWarmingPotential] = None
    GWP_total: list[float] = None
    GWP_mean: float = None

    def __post_init__(self):
        if self.short_label is None:
            self.short_label = self.name  # set short_label to name if not given.

        # Instantiate object with default values and calculate its GWP and TEA results
        if self.instantiate_with_default_reqs:
            self.instantiate_default_requirements()
            self.calculate_GWP()
            self.calculate_TEA()

    def add_subprocess(self, subprocess, update_results=True):
        """
        Add a new subprocess to current process object.
        Parameters
        ----------
        subprocess: Type[Process]
            Process object which is to be added as a subprocess.
        update_results: bool
            Determines whether results should be updated based on newly added subprocess.
        """
        self.subprocesses += (subprocess, )

        if update_results:
            self.calculate_GWP()
            self.calculate_TEA()
        else:
            raise Warning("Recalculate GWP and TEA results for main process to take into account subprocesses.")

    def add_requirements(self, requirements):
        """
        Add a new "Requirements" object to current process object.

        Parameters
        ----------
        requirements: Requirements
            Requirements object which is to be added as a subprocess.
        """
        self.requirements += (requirements, )

    def instantiate_default_requirements(self):
        """
        Placeholder function.
        Instantiate process object with default requirements. Will vary for every process.
        """
        raise NotImplementedError("Child class should implement this function.")

    def calculate_requirements(self):
        """
        Placeholder function.
        Used to calculate the process requirements. Generally executing without inputs will fetch default values.
        """
        pass

    def calculate_GWP(self, consider_subprocesses=True):
        """
        Convert a processes requirements to their corresponding Global Warming Potential (GWP).

        Parameters
        ----------
        consider_subprocesses: bool
            Indicates whether subprocess requirements should be considered too.

        Returns
        -------
        tuple[GlobalWarmingPotential]
            Global warming potentials resulting from process requirements.
        """
        self.GWP_results = process_requirements_to_GWP(self.requirements)  # calculate GWP for process' requirements.

        if consider_subprocesses:  # add requirements in subprocess.
            # Consider subprocesses
            for subprocess_no in range(len(self.subprocesses)):
                if self.subprocesses[subprocess_no].GWP_results is None:  # Calculate from requirements
                    self.GWP_results += process_requirements_to_GWP(self.subprocesses[subprocess_no].requirements)
                else:  # add if already calculated
                    self.GWP_results += self.subprocesses[subprocess_no].GWP_results
                # Consider sub-subprocesses
                for sub_subprocess_no in range(len(self.subprocesses[subprocess_no].subprocesses)):
                    if self.subprocesses[subprocess_no].subprocesses[sub_subprocess_no].GWP_results is None:
                        self.GWP_results += process_requirements_to_GWP(self.subprocesses[subprocess_no].
                                                                        subprocesses[sub_subprocess_no].requirements)
                    else:
                        self.GWP_results += self.subprocesses[subprocess_no].subprocesses[sub_subprocess_no].GWP_results

                    # Check that no deeper nested subprocesses exist
                    if self.subprocesses[subprocess_no].subprocesses[sub_subprocess_no].subprocesses != ():
                        raise Warning("Deeper nested subprocesses may exist and have not been considered.")

        # Calculate total GWP
        GWP_lists = []
        for GWP_obj in self.GWP_results:
            GWP_lists.append(GWP_obj.values)
        self.GWP_total = list(np.array([sum(x) for x in zip(*GWP_lists)]).flatten())
        self.GWP_mean = float(np.mean(self.GWP_total))

    def calculate_TEA(self, consider_nested=True):
        pass

    def plot_GWP(self, bins=40, stacked=True, show_total=True, short_labels=False):
        """
        Plot histogram of the process' and its subprocess' GWP.

        Parameters
        ----------
        bins: int
            Number of bins for histogram.
        stacked: bool
            Show interfering bars as stacked or overlapping.
        show_total: bool
            Show total GWP of process in addition to subprocesses.
        short_labels: bool
            Determines whether shorthand labels or full labels should be used.
        Returns
        -------
        matplotlib.pyplot.axes
            Matplotlib axis object.
        """

        # Get required parameters
        subprocess_names = []
        subprocess_short_labels = []
        subprocess_GWPs = []
        for count in range(len(self.GWP_results)):
            subprocess_names.append(self.GWP_results[count].name)
            subprocess_short_labels.append(self.GWP_results[count].short_label)
            subprocess_GWPs.append(self.GWP_results[count].values)

        # Convert to right format
        subprocess_GWPs = np.transpose(np.array(subprocess_GWPs))

        # Get marker coordinates to show "Total"
        marker_x = None
        marker_y = None
        marker_threshold = None
        if show_total:
            GWP_total = np.array(self.GWP_total)
            marker_x = np.array(plt.hist(GWP_total, bins=bins, alpha=0, histtype='bar')[1][0:-1])
            marker_y = np.array(plt.hist(GWP_total, bins=bins, alpha=0, histtype='bar')[0])
            # set threshold below which markers are not displayed
            marker_threshold = settings.background.iterations_MC * 0.01
            plt.clf()  # to prevent interference with actual plot

        # Plot
        sns.set_theme()
        fig, ax = plt.subplots()
        if not short_labels:
            ax.hist(subprocess_GWPs, bins=bins, histtype='bar', stacked=stacked, alpha=1, label=subprocess_names)
        else:
            ax.hist(subprocess_GWPs, bins=bins, histtype='bar', stacked=stacked, alpha=1,
                    label=subprocess_short_labels)

        # Plot total whilst excluding zeros or very low values for plotting
        if show_total:
            ax.scatter(marker_x[marker_y > marker_threshold], marker_y[marker_y > marker_threshold], label="Total",
                       marker="x", color="black", alpha=0.8)

        # Set legend, title, and labels
        ax.legend()
        ax.set_title(self.name)
        ax.set_xlabel(settings.labels.LCA_output_plotting_string)
        ax.set_ylabel("Monte Carlo Iterations")

        # Display plot
        plt.tight_layout()
        plt.show()

    def plot_TEA(self):
        pass

    def plot_results(self, show_GWP=True, show_TEA=True):
        if show_GWP:
            self.plot_GWP()
        if show_TEA:
            self.plot_TEA()