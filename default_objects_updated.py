from collections import namedtuple
from dataclasses import dataclass, field

# Define requirement named tuples

electricity = namedtuple("electricity", ["values", "name", "short_label", "units", "source", "description"],
                         defaults=[None, "kWh", "grid", None],
                         module="requirements")

heat = namedtuple("heat", ["values", "name", "short_label", "units", "source", "description"],
                  defaults=[None, "kWh", "natural gas", None],
                  module="requirements")

oxygen = namedtuple("oxygen", ["values", "name", "short_label", "units", "source", "description"],
                    defaults=[None, "kg", "ASU", None],
                    module="requirements")

steam = namedtuple("steam", ["values", "name", "short_label", "units", "source", "description"],
                   defaults=[None, "kg", "default", None],
                   module="requirements")

GWP_direct = namedtuple("GWP_direct", ["values", "name", "short_label", "units", "source", "description"],
                        defaults=[None, "kg CO2eq.", "fossil", None],
                        module="requirements")

costs = namedtuple("cost", ["values", "name", "short_label", "units", "source", "description"],
                   defaults=[None, "£", None, None],
                   module="requirements")

benefit = namedtuple("benefit", ["values", "name", "short_label", "units", "source", "description"],
                     defaults=[None, "£", None, None],
                     module="requirements")

test_electricity = electricity(values=[20, 20, 20], name="test process")


# Dataclass to store process requirements
@dataclass
class requirements:
    """ Intermediate dataclass to store process requirements for a process and its subprocesses."""
    # electricity = namedtuple("electricity", ["values", "name", "short_label", "units", "source", "description"],
    #                          defaults=[None, "kWh", "grid", None],
    #                          module="requirements")

    electricity: tuple[electricity] = ()
    heat: tuple[electricity] = ()
    oxygen: tuple[electricity] = ()
    steam: tuple[electricity] = ()
    GWP_direct: tuple[GWP_direct] = ()
    costs: tuple[costs] = ()
    benefit: tuple[benefit] = ()

    # uses same names for tuple type and class property - probs not best

    def add_requirement(self, requirement_object, object_type=None):
        if object_type is None:
            object_type = str(type(requirement_object))
            # automatically find type of object - should be named tuple of certain type which then allows it to be assigned to the correct requirements tuple
            # type checking generally a bad idea - maybe think of a work around http://www.canonical.org/~kragen/isinstance/

        if isinstance(object_type, requirements.electricity):
            pass

        #from default_objects_updated import electricity
        """Add the name and GWP of a new subprocess to dataclass object."""

        #from default_objects_updated import electricity
        if isinstance(requirement_object, electricity):
            self.electricity += (requirement_object,)
        else:
            print("comparison unsuccessful")


test_req_object = requirements()
test_req_object.add_requirement(requirement_object=test_electricity)

print(isinstance(test_electricity, electricity))
"""
example of how isistance could be used to check type
class MyClass:
    _message = "Hello World"

_class = MyClass()

print("_class is a instance of MyClass() : ", isinstance(_class,MyClass))


"""


# Dataclass to store process requirements
@dataclass
class process:
    """Description."""
    process_name: str
    information: str
    subprocesses: list["process"]  # wrap name in string to forward declare - alternatively could use from __future__
    # import annotations
    requirements = list[requirements]

    from configs.default_objects import process_GWP_output_MC  # won't be necessary if I put them all in same file eventually
    GWP_results = process_GWP_output_MC
    # TEA_results = process_TEA_output_MC


    def add_subprocess(self):
        pass

    def add_requirements(self):
        pass

    def get_default_requirements(self, replace=True):
        """

        Parameters
        ----------
        replace: bool
            Determine whether existing requirements should be replaced or updated by defaults.

        Returns
        -------

        """
        pass

    def calculate_GWP(self, consider_nested=True):
        """
        will need way to go into nested structure and evaluate GWP for each subprocess and their subprocesses...
        Returns
        -------

        """
        pass

    def calculate_TEA(self):
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