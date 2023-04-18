import pickle

import numpy as np

from functions.general.utility import get_project_root


def load_air_separation_unit_data(full_file_path=None):
    """
    Load pickled data done in analysis on air separation unit electricity demands.
    Analysis done in: analysis/preliminary/air_separation_unit/air_separation_unit_comparison.ipynb.

    Parameters
    ----------
    full_file_path: str
        "r" string specifying the file path to pickle object.

    Returns
    -------
    dict
        Loaded air separation unit data
    """
    if full_file_path is None:
        project_root = get_project_root()
        full_file_path = str(project_root) + r"\data\air_separation_unit_results"

    # Load pickled data
    loaded_data = pickle.load(open(full_file_path, "rb"))

    return loaded_data


def oxygen_rng_elect_req(mass_oxygen):
    """
    Generates a randomised electricity requirement of an air separation unit (ASU) for the provision of oxygen based
    on a normal distribution defined by literature values.

    Parameters
    ----------
    mass_oxygen: float
        Required mass of oxygen. [kg]

    Returns
    -------
    float
        Randomised electricity requirement of ASU for oxygen production [kWh el].
    """

    # Get data - More info in analysis - air_separation_unit_comparison.ipynb
    data = load_air_separation_unit_data()
    mean = data["Mean"]  # [kWh el./Nm3 O2]
    std = data["Std"]  # [kWh el./Nm3 O2]

    # Generate random value
    value = np.random.normal(mean, std) * mass_oxygen  # [kWh el]

    return value
