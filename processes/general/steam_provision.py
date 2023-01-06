import pickle

import numpy as np

from config import settings
from functions.general.utility import kJ_to_kWh


def load_boiler_efficiency_data(full_file_path=r"C:\Users\2270577A\PycharmProjects\PhD_LCA_TEA\data"
                                                 r"\boiler_efficiency_results"):
    """
    Load pickled data done in analysis on boiler efficiency for steam production.
    Analysis done in: analysis/preliminary/boiler_efficiency/boiler_efficiency.ipynb.

    Parameters
    ----------
    full_file_path: str
        "r" string specifying the file path to pickle object.

    Returns
    -------
    dict
        Loaded boiler efficiency data
    """

    # Load pickled data
    loaded_data = pickle.load(open(full_file_path, "rb"))
    # TODO: Change call to file path to dynamic call - could try something like sys.path[-1]

    return loaded_data


def steam_rng_heat_req(mass_steam, FU=settings.general.FU):
    """
    Calculates heat requirement for steam production after applying some uncertainty.

    Parameters
    ----------
    mass_steam: float
        Required mass of steam.

    Returns
    -------
    float
        Randomised heat requirement for steam production [kWh th./ FU].
    """

    # Get some reference parameters
    room_temperature = settings.data.feedstock_drying.room_temperature  # in deg C
    boiling_temperature = 100  # in deg C

    # Calculate theoretical heat requirements
    heat_raise = (boiling_temperature - room_temperature) * settings.data.specific_heats["water"]  # [kJ/kg]
    heat_vaporisation = settings.data.heats_vaporisation.water["100 degC"]  # [kJ/kg]
    unit_heat_required = heat_raise + heat_vaporisation  # in kJ/kg steam
    total_theoretical_heat_required_kJ = unit_heat_required * mass_steam * FU  # [kJ/FU]
    total_theoretical_heat_required = kJ_to_kWh(total_theoretical_heat_required_kJ)  # [kWh/FU]

    # Get boiler efficiency
    boiler_efficiency_data = load_boiler_efficiency_data()
    lower_efficiency = boiler_efficiency_data['triangular distribution values'].lower
    mode_efficiency = boiler_efficiency_data['triangular distribution values'].mode
    upper_efficiency = boiler_efficiency_data['triangular distribution values'].upper

    # Apply boiler efficiency

    randomised_boiler_efficiency = np.random.triangular(left=lower_efficiency,
                                                        mode=mode_efficiency,
                                                        right=upper_efficiency)

    randomised_heat_req = total_theoretical_heat_required * 1/randomised_boiler_efficiency

    return randomised_heat_req
