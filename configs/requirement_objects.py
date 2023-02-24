import numpy as np

from dataclasses import dataclass
from config import settings


# Define requirement parent class
@dataclass(kw_only=True)
class _Requirement:
    """
    Requirements parent class used to instantiate new requirement subclasses.

    Attributes
    ----------
    values: list[float]
        The actual requirements where the list is the length of Monte Carlo iterations.
    name : str
        The name of the requirement.
    short_label : str
        A short label of the requirement - used for plotting etc.
    units: str
        The units of the requirement values.
    description: str
        Optional description can be added here.
    source: str
        Used to define the source of the requirement. E.g. is electricity coming from the grid or another source.
    """

    values: list[float]
    name: str
    short_label: str = None
    units: str = None
    description: str = None
    source: str = None

    def __post_init__(self):
        if self.short_label is None:
            self.short_label = self.name  # set short_label to name if not given.

        if len(self.values) == 1 and settings.background.iterations_MC != 1:
            self.values = list(np.array(self.values).flatten())  # flatten if required

# Define requirement child classes
# Energy Use
@dataclass(kw_only=True)
class Electricity(_Requirement):
    # Update defaults
    name: str = "Electricity consumption"
    short_label: str = "Ele."
    units: str = "kWh"
    source: str = "grid"
    generated: bool = False


@dataclass(kw_only=True)
class Heat(_Requirement):
    # Update defaults
    name: str = "Heat use"
    short_label: str = "Heat"
    units: str = "kWh"
    source: str = "natural gas"
    generated: bool = False


# Direct environmental factors
@dataclass(kw_only=True)
class FossilGWP(_Requirement):
    # Update defaults
    name: str = "Fossil CO2 eq."
    units: str = "kg CO2eq."
    negative_emissions: bool = False

    def __post_init__(self):
        if self.negative_emissions is True:
            if all(x >= 0 for x in self.values):  # check if values given as positives
                self.values = [-x for x in self.values]  # turn into negatives
                raise Warning("Negative emission values were given as positives - turned into negatives.")


@dataclass(kw_only=True)
class BiogenicGWP(_Requirement):
    """
    Biogenic carbon emissions or global warming potential impact.

    Attributes
    ----------
    values: list[float]
        Carbon emissions before accounting for biogenic nature of carbon.
    name : str
    short_label : str
    units: str
    description: str
    source: str
    biogenic_fraction: float
        Determines how biogenic emissions are supposed to be treated:
        0 - completely biogenic (i.e. no net GWP) | 1 - equivalent to fossil fuels
    negative_emissions: bool
        Ensures values are given as negative and always sets biogenic_fraction to 1.
    """

    # Update defaults
    name: str = "Biogenic CO2 eq."
    units: str = "kg CO2eq."

    # Add new parameters
    biogenic_fraction: float = settings.background.biogenic_carbon_equivalency
    negative_emissions: bool = False

    def __post_init__(self):
        if self.negative_emissions is True:
            self.biogenic_fraction = 1  # to ensure benefit is accounted for.

            if all(x >= 0 for x in self.values):  # check if values given as positives
                self.values = [-x for x in self.values]  # turn into negatives
                raise Warning("Negative emission values were given as positives - turned into negatives.")


# Economics - costs and benefits
@dataclass(kw_only=True)
class Cost(_Requirement):
    # Update defaults
    name: str = "Cost"
    units: str = "GBP"


@dataclass(kw_only=True)
class Benefit(_Requirement):
    # Update defaults
    name: str = "Benefit"
    units: str = "GBP"


# Other requirements
@dataclass(kw_only=True)
class Oxygen(_Requirement):
    # Update defaults
    name: str = "Oxygen"
    short_label: str = "O2"
    units: str = "kg"
    source: str = "grid"  # i.e. electricity used


@dataclass(kw_only=True)
class Steam(_Requirement):
    # Update defaults
    name: str = "Steam"
    short_label: str = "Steam"
    units: str = "kg"
    source: str = "natural gas"  # i.e. heat used


# Define Requirements class which all kinds of _Requirement children can be added to.
@dataclass
class Requirements:
    """
    Stores a range of process requirements. Attributes are children of _Requirement class.


    Attributes
    ----------
    name: str
    electricity: tuple[Electricity]
    heat: tuple[Heat]
    fossil_GWP: tuple[FossilGWP]
    biogenic_GWP: tuple[BiogenicGWP]
    cost: tuple[Cost]
    benefit: tuple[Benefit]
    steam: tuple[Steam]
    oxygen: tuple[Oxygen]

    Methods
    ------
    add_requirement(requirement_object)
        Adds a new "requirement" to this "Requirements" object.
        "requirement" objects are children of the "_Requirement" class.
    """
    name: str

    # Energy Use
    electricity: tuple[Electricity] = ()
    heat: tuple[Heat] = ()
    # Direct environmental factors
    fossil_GWP: tuple[FossilGWP] = ()
    biogenic_GWP: tuple[BiogenicGWP] = ()

    # Economics - costs and benefits
    cost: tuple[Cost] = ()
    benefit: tuple[Benefit] = ()

    # Other requirements
    steam: tuple[Steam] = ()
    oxygen: tuple[Oxygen] = ()

    def add_requirement(self, requirement_object):
        """
        Adds a new "requirement" to this "Requirements" object.
        "requirement" objects are children of the "_Requirement" class.
        Parameters
        ----------
        requirement_object: Electricity | Heat | FossilGWP | BiogenicGWP | Cost | Benefit | Steam | Oxygen
            Requirement object (i.e. Type[_Requirement]).
        """

        # Add requirement object to correct tuple.
        if isinstance(requirement_object, Electricity):
            self.electricity += (requirement_object, )

        elif isinstance(requirement_object, Heat):
            self.heat += (requirement_object, )

        elif isinstance(requirement_object, FossilGWP):
            self.fossil_GWP += (requirement_object, )

        elif isinstance(requirement_object, BiogenicGWP):
            self.biogenic_GWP += (requirement_object, )

        elif isinstance(requirement_object, Cost):
            self.cost += (requirement_object, )

        elif isinstance(requirement_object, Benefit):
            self.benefit += (requirement_object, )

        elif isinstance(requirement_object, Steam):
            self.steam += (requirement_object, )

        elif isinstance(requirement_object, Oxygen):
            self.oxygen += (requirement_object, )

        else:
            raise ValueError("Wrong requirement object supplied. Ensure supported type is used.")
