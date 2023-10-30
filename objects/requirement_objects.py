import warnings

import numpy as np

from dataclasses import dataclass
from config import settings
from typing import Literal


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
        # Set short_label to name if not given.
        if self.short_label is None:
            self.short_label = self.name

        # Flatten values if required
        if len(self.values) == 1 and settings.user_inputs.general.MC_iterations != 1:
            self.values = list(np.array(self.values).flatten())


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
    """
    Fossil carbon emissions or global warming potential impact.

    Attributes
    ----------
    values: list[float]
        Carbon emissions before accounting for biogenic nature of carbon.
    name : str
    short_label : str
    units: str
    description: str
    source: str
    negative_emissions: bool
        Ensures values are given as negative and always sets biogenic_fraction to 1.
    """

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
                warnings.warn("Negative emission values were given as positives - turned into negatives.")


_tag_options = Literal[None, "CAPEX", "O&M", "Other operational expenses", "Sale of products", "Other form of income",
                       "Transport", "Other", "Not classified"]


# Direct cash flows
@dataclass
class _ParentPresentAnnualFutureValue(_Requirement):
    """
    Parent class for present, annual, and future value classes.

    Attributes
    ----------
    values: list[float]
        The cash flows distribution for Monte Carlo simulation where the list is the length of Monte Carlo iterations.
    name : str
        The name of the cash flow.
    short_label : str
        A short label of the cash flow - used for plotting etc.
    currency: str
        The currency of the cash flows.
    rate_of_return: float
        Given as a decimal. Note the rate of return, interest rate, and discount rate are used interchangeably in
        this context. Used to convert between PV, AV, and FV.
    number_of_periods: int
        Used to convert between PV, AV, and FV. Typically, the system's life cycle.
    tag: _tag_options
        Identifier to categorise cost and benefit objects.
    description: str
        Optional description can be added here.
    """
    currency: str = None
    rate_of_return: float = None
    number_of_periods: int = None
    tag: _tag_options = None

    def __post_init__(self):
        # Set short_label to name if not given.
        if self.short_label is None:
            self.short_label = self.name

        # Flatten values if required
        if len(self.values) == 1 and settings.user_inputs.general.MC_iterations != 1:
            self.values = list(np.array(self.values).flatten())

        if self.currency is None:
            self.currency = settings.user_inputs.general.currency

        if self.rate_of_return is None:
            self.rate_of_return = settings.user_inputs.economic.rate_of_return_decimals

        if self.number_of_periods is None:
            self.number_of_periods = settings.user_inputs.general.system_life_span


@dataclass
class PresentValue(_ParentPresentAnnualFutureValue):
    """
    Also called present worth.
    """


class AnnualValue(_ParentPresentAnnualFutureValue):
    """
    Also called annual worth or annuity.
    """


class FutureValue(_ParentPresentAnnualFutureValue):
    """
    Also called future worth.
    """


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
    cash_flow_pv: tuple[PresentValue]
    cash_flow_av: tuple[AnnualValue]
    cash_flow_fv: tuple[FutureValue]
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

    # Direct cash flows
    cash_flow_pv: tuple[PresentValue] = ()
    cash_flow_av: tuple[AnnualValue] = ()
    cash_flow_fv: tuple[FutureValue] = ()

    # Other requirements
    steam: tuple[Steam] = ()
    oxygen: tuple[Oxygen] = ()

    def add_requirement(self, requirement_object):
        """
        Adds a new "requirement" to this "Requirements" object.
        "requirement" objects are children of the "_Requirement" class.
        Parameters
        ----------
        requirement_object: Electricity | Heat | FossilGWP | BiogenicGWP | PresentValue | AnnualValue| FutureValue| Steam | Oxygen
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

        elif isinstance(requirement_object, PresentValue):
            self.cash_flow_pv += (requirement_object,)

        elif isinstance(requirement_object, AnnualValue):
            self.cash_flow_av += (requirement_object,)

        elif isinstance(requirement_object, FutureValue):
            self.cash_flow_fv += (requirement_object,)

        elif isinstance(requirement_object, Steam):
            self.steam += (requirement_object, )

        elif isinstance(requirement_object, Oxygen):
            self.oxygen += (requirement_object, )

        else:
            raise ValueError("Wrong requirement object supplied. Ensure supported type is used.")
