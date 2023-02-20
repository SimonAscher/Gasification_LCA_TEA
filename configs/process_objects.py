import numpy as np

from dataclasses import dataclass, InitVar
from configs.requirement_objects import _Requirement, Requirements
from typing import Type
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
    # TODO: Update type hint so it properly shows children of _Requirement class.

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

    def add_subprocess(self, subprocess):
        """
        Add a new subprocess to current process object.
        Parameters
        ----------
        subprocess: Type[Process]
            Process object which is to be added as a subprocess.
        """
        self.subprocesses += (subprocess, )

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
                self.GWP_results += process_requirements_to_GWP(self.subprocesses[subprocess_no].requirements)
                # Consider sub-subprocesses
                for sub_subprocess_no in range(len(self.subprocesses[subprocess_no].subprocesses)):
                    self.GWP_results += process_requirements_to_GWP(self.subprocesses[subprocess_no].
                                                                    subprocesses[sub_subprocess_no].requirements)
                # TODO: Add check here to see if GWP had already been calculated - if so just use that
        # Calculate total GWP
        GWP_lists = []
        for GWP_obj in self.GWP_results:
            GWP_lists.append(GWP_obj.values)
        self.GWP_total = [sum(x) for x in zip(*GWP_lists)]
        self.GWP_mean = float(np.mean(self.GWP_total))

    def calculate_TEA(self, consider_nested=True):
        pass

    def plot_results(self, plot_GWP=False, plot_TEA=False, plot_type_GWP=None, plot_type_TEA=None):
        """
        Need options to plot either GWP or TEA or both and then specify desired plot types for either.
        Can also ommit this as I already have plotting functions elsewhere...

        types - sankey diagram, histograms, MC results, average distributions,etc.

        Parameters
        ----------
        plot_GWP
        plot_TEA
        plot_type

        Returns
        -------

        """
        pass
