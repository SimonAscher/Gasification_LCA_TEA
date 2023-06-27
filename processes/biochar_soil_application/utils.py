import pickle

import numpy as np

from config import settings
from functions.general.utility import get_project_root

def load_biochar_properties_data(full_file_path=None):
    """
    Load pickled data done in analysis on biochar properties (e.g. carbon fraction and carbon stability)
    Analysis done in: analysis/preliminary/biochar_properties/biochar_properties.ipynb.

    Parameters
    ----------
    full_file_path: str
    "r" string specifying the file path to pickle object.

    Returns
    -------
    dict
        Loaded data on biochar properties.
    """
    if full_file_path is None:
        project_root = get_project_root()
        full_file_path = str(project_root) + r"\data\biochar_properties_results"

    # Load pickled data
    loaded_data = pickle.load(open(full_file_path, "rb"))

    return loaded_data


def avoided_N2O_emissions(biochar_yield):
    """
    Avoided N20 emissions due to applying biochar to soil.

    Parameters
    ----------
    biochar_yield: float
        Biochar yield [kg/FU].

    Returns
    -------
    float
        Reduction in N2O release from soil after biochar application [kg N2O/FU].

    """
    # Data: https://doi.org/10.1371/journal.pone.0176111
    soil_emissions_mean = 2.27  # kg N ha^-1 yr^-1
    soil_emissions_1st_quartile = 1.18  # kg N ha^-1 yr^-1
    soil_emissions_3rd_quartile = 2.63  # kg N ha^-1 yr^-1

    soil_emissions_std_1 = (soil_emissions_mean - soil_emissions_1st_quartile) / 0.675
    soil_emissions_std_2 = (-soil_emissions_mean + soil_emissions_3rd_quartile) / 0.675
    soil_emissions_std_avg = (soil_emissions_std_1 + soil_emissions_std_2) / 2

    # Scaling factor to scale N emissions to N2O emissions
    N_to_N2O = (settings.data.molar_masses.N + 2 * settings.data.molar_masses.O) / settings.data.molar_masses.N

    # Data (Supplementary Material 2 https://doi.org/10.1371/journal.pone.0176111)
    N2O_reduction_factor = 0.30  # i.e. 30%
    application_rate = 25000  # kg ha^-1 yr^-1

    # Generate random unit value
    emission_rng = np.random.normal(soil_emissions_mean * N_to_N2O,
                                    soil_emissions_std_avg * N_to_N2O)  # kg N2O ha^-1 yr^-1

    avoided_N20_emissions = (-1 * emission_rng * N2O_reduction_factor * biochar_yield) / 25000  # N20

    return avoided_N20_emissions
