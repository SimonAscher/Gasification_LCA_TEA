from collections import namedtuple
from dataclasses import dataclass
from config import settings

# Named tuple objects - used for making distributions for Monte Carlo simulation
fixed_dist_maker = namedtuple("fixed_dist_maker", "value")
range_dist_maker = namedtuple("range_dist_maker", "low high")
triangular_dist_maker = namedtuple("triangular_dist_maker", "lower mode upper")
gaussian_dist_maker = namedtuple("gaussian_dist_maker", "mean std")


@dataclass
class _ParentPresentAnnualFutureValue:
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
    units: str
        The units of the cash flows (i.e. currency).
    rate_of_return: float
        Given as a decimal. Note the rate of return, interest rate, and discount rate are used interchangeably in
        this context. Used to convert between PV, AV, and FV.
    number_of_periods: int
        Used to convert between PV, AV, and FV. Typically, the systems life-cycle.
    description: str
        Optional description can be added here.
    """
    values: list[float]
    name: str
    short_label: str = None
    units: str = None
    rate_of_return: float = None
    number_of_periods: int = None
    description: str = None

    def __post_init__(self):
        if self.short_label is None:  # Set short_label to name if not given.
            self.short_label = self.name

        if self.units is None:
            self.units = settings.user_inputs.general.currency

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
