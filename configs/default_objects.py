from collections import namedtuple
from dataclasses import dataclass, field
from typing import Union
from functions.LCA import thermal_energy_GWP, electricity_GWP
import warnings

# Named tuple objects - used for making distributions for Monte Carlo simulation
triangular = namedtuple("triangular", "lower mode upper")
gaussian = namedtuple("gaussian", "mean sigma")


@dataclass
class process_GWP_output:
    """ Dataclass to store individual GWP results of a process and its subprocesses."""
    # Process name, overall GWP of process and GWP when not accounting for biogenic nature of carbon.
    process_name: str
    GWP: float = 0
    GWP_from_biogenic: float = 0

    # Tuples to store names and respective emissions of subprocesses.
    subprocess_names: tuple[str] = ()
    subprocess_GWP: tuple[float] = ()

    units: str = "kg CO2eq./FU"

    def add_subprocess(self, name: str, GWP: float):
        """Add the name and GWP of a new subprocess to dataclass object."""
        self.subprocess_names += (name, )
        self.subprocess_GWP += (GWP, )

    def calculate_GWP_from_subprocesses(self):
        """Calculate process' overall GWP from the GWPs of its subprocesses."""
        total_GWP = sum(self.subprocess_GWP)
        self.GWP = total_GWP

        # Raise error if calculated value does not agree with previously given value.
        if isinstance(self.GWP, (int, float)) and self.GWP != total_GWP:
            warnings.warn("GWP calculated from subprocesses does not equal initially given GWP.")


@dataclass
class process_GWP_output_MC:
    """ Dataclass to store all Monte Carlo simulation results for a process' GWP calculations."""
    process_name: str
    subprocess_abbreviations: tuple[str] = ()  # abbreviations of subprocesses used for plotting
    simulation_results: tuple[process_GWP_output] = ()  # Stores results objects.
    simulation_parameters: tuple[list] = ()  # Stores simulation parameters.

    def add_GWP_object(self, process_GWP_output_object: object):
        """Add a new GWP object of one Monte Carlo iteration."""
        self.simulation_results += (process_GWP_output_object, )

    def add_variables_info(self, name, value, units: str = "default"):
        """Store the name, value, and units of varying parameters for the given MC iteration."""
        self.simulation_parameters += ([name, value, units], )
        # TODO: Currently works fine when adding just one simulation parameter - or when calling the function just once
        #  with nested lists. I.e. (value = ["Electricity", "Efficiency], value = [200, 0.40]). Bug when calling
        #  function multiple times within one MC iteration.


# Dataclass to store process requirements
@dataclass
class process_requirements:
    """ Intermediate dataclass to store process requirements for a process and its subprocesses."""
    # Process name, overall GWP of process and GWP when not accounting for biogenic nature of carbon.
    name: str

    # Tuples to store names and respective emissions or requirements of subprocesses.
    subprocess_names: tuple[str] = ()
    subprocess_direct_GWP: tuple[float] = ()
    subprocess_heat: tuple[float] = ()
    subprocess_electricity: tuple[float] = ()
    subprocess_total_GWP: tuple[float] = ()

    units_GWP: str = "kg CO2eq./FU"
    units_other: str = "kWh/FU"

    def add_subprocess(self, name: str, GWP: float = 0, heat: float = 0, electricity: float = 0):
        """Add the name and GWP of a new subprocess to dataclass object."""
        self.subprocess_names += (name,)
        self.subprocess_direct_GWP += (GWP,)
        self.subprocess_heat += (heat,)
        self.subprocess_electricity += (electricity,)

        # Calculate total GWP
        total_GWP = GWP + thermal_energy_GWP(amount=heat) + electricity_GWP(amount=electricity)
        self.subprocess_total_GWP += (total_GWP,)


"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   NOTES   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Other useful functionality of data classes is explained here: https://realpython.com/python-data-classes/
    - things like __post_init__ to calculate parameters after initialising the class might be most useful
"""
