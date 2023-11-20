import pickle
import warnings

import numpy as np

from config import settings
from functions.general.utility import kJ_to_kWh, get_project_root


def energy_drying(mass_feedstock=None,
                  moisture_ar=None,
                  moisture_post_drying=None,
                  dryer_type=None,
                  specific_heat_reference_temp=None,
                  electricity_reference=None,
                  output_unit=None,
                  syngas_as_fuel=False,
                  show_values=False
                  ):
    """
    Function used to calculate the energy requirements to dry a feedstock.

    Parameters
    ----------
    mass_feedstock: float
        Initial feedstock mass on an as received basis [kg].
    moisture_ar: float
        Moisture content of feedstock before drying (i.e. as received basis) as a percentage.
    moisture_post_drying: float
        Desired moisture content of feedstock after drying as a percentage.
    dryer_type: str
        Defines which dryer type is to be used. This effects the efficiency of the drying process and the energy source
        used to provide the heat.
    specific_heat_reference_temp: str
        Defines which references temperature should be used for the specific latent heat of vaporisation and
        specific heat of water vapor.
    electricity_reference: str
        Defines which source should be used to base electricity calculations on.
    output_unit: str
        Defines the output unit e.g. kWh or kJ.
    syngas_as_fuel: bool
        Defines if some produced syngas should be used for heating purposes.
    show_values: bool
        Use "True" to print calculations.

    Returns
    -------
    dict
        Dictionary of energy requirements in the form of heat and electricity including their sources and the units.
        Note: Heat requirement given as amount of raw heat source required (e.g. XYZ kWh of natural gas)
    """
    # Get defaults
    if mass_feedstock is None:
        mass_feedstock = settings.general.FU
    if moisture_ar is None:
        moisture_ar = settings.user_inputs.feedstock.moisture_ar
    if moisture_post_drying is None:
        moisture_post_drying = settings.user_inputs.feedstock.moisture_post_drying
    if dryer_type is None:
        dryer_type = settings.user_inputs.processes.drying.dryer_type
    if specific_heat_reference_temp is None:
        specific_heat_reference_temp = settings.user_inputs.processes.drying.specific_heat_reference_temp
    if electricity_reference is None:
        electricity_reference = settings.user_inputs.processes.drying.electricity_reference
    if output_unit is None:
        output_unit = settings.user_inputs.processes.drying.output_unit

    # Get data and reference values from settings
    # Assumed room temperature and temperature of drying process
    temp_drying_process = settings.data.feedstock_drying.temp_drying_process  # in deg C
    room_temperature = settings.data.feedstock_drying.room_temperature  # in deg C

    # Specific latent heats of vaporisation of water
    heat_vaporisation = settings.data.heats_vaporisation.water

    # Specific heats of water vapor
    heat_water_vapor = settings.data.specific_heats.water_vapor

    # Efficiencies of different dryer types
    dryer_efficiencies = settings.data.feedstock_drying.dryer_efficiencies

    # Electricity requirements for auxiliary processes (Note difference in units)
    electricity_requirements = settings.data.feedstock_drying.electricity_requirements

    # Check for erroneous inputs
    if moisture_ar < 1 or moisture_post_drying < 1:
        raise ValueError("Ensure that moisture contents are given as percentages.")
    if moisture_ar < moisture_post_drying:
        raise ValueError("Warning: Moisture content of as received feedstock must be higher than moisture content "
                         "post drying.")

    # Turn moisture's from percentages to decimals
    moisture_ar /= 100
    moisture_post_drying /= 100

    # Calculate mass of evaporated water:
    mass_water_initial = mass_feedstock * moisture_ar
    mass_feed_dry = mass_feedstock * (1 - moisture_ar)
    mass_water_post_drying = (mass_feed_dry * moisture_post_drying) / (1 - moisture_post_drying)
    mass_feedstock_post_drying = mass_feed_dry + mass_water_post_drying
    mass_evaporated_water = mass_water_initial - mass_water_post_drying

    # Heat requirement:
    # Calculate theoretical heat for drying
    heat_drying = heat_vaporisation[specific_heat_reference_temp] * mass_evaporated_water + heat_water_vapor[
        specific_heat_reference_temp] * abs(temp_drying_process - room_temperature) * mass_evaporated_water
    # Add penalty due to dryer inefficiency
    heat_drying_post_dryer_efficiency = heat_drying / dryer_efficiencies[dryer_type]

    # Electricity requirement:
    # Calculate auxiliary energy requirements (electricity) for screw feeders, pumps, fans, etc.
    electricity_drying = []

    if electricity_reference == 'GaBi (mean)':
        electricity_drying = electricity_requirements[electricity_reference] * mass_feedstock

    elif electricity_reference == 'Huber Belt dryer':
        electricity_drying = electricity_requirements[electricity_reference] * mass_evaporated_water

    # Determine fuel source for drying
    energy_source_drying = []

    if dryer_type == 'Indirect-heated convection dryer' or dryer_type == 'Contact dryer' or \
            dryer_type == 'Direct fired dryer':
        energy_source_drying = 'natural gas'

        # Overwrite energy_source if Syngas is to be used for drying
        if syngas_as_fuel:
            energy_source_drying = 'syngas'

    elif dryer_type == 'Microwave drying':
        energy_source_drying = 'electricity'

    energies_out = []

    if dryer_type == "Solar drying":
        energies_out = {"heat": 0,
                        "electricity": 0,
                        "heat source": "Solar",
                        "units": output_unit
                        }
    else:
        if output_unit == "kWh":
            energies_out = {"heat": kJ_to_kWh(heat_drying_post_dryer_efficiency),
                            "electricity": electricity_drying,
                            "heat source": energy_source_drying,
                            "units": output_unit
                            }
        elif output_unit == "kJ":
            energies_out = {"heat": heat_drying_post_dryer_efficiency,
                            "electricity": kJ_to_kWh(electricity_drying, reverse=True),
                            "heat source": energy_source_drying,
                            "units": output_unit
                            }

    # Print calculations if desired
    if show_values:
        # Evaporated water calculations:
        print('Mass of initial feedstock:', mass_feedstock, '[kg]')
        print('Mass of water in initial feedstock:', mass_water_initial, '[kg]')
        print('Mass of dry material in feedstock at 0 % moisture:', mass_feed_dry, '[kg]')
        print('Mass of water in feedstock post drying:', mass_water_post_drying, '[kg]')
        print('Mass of evaporated water:', mass_evaporated_water, '[kg]')
        print('Mass of feedstock post drying:', mass_feedstock_post_drying, '[kg]')
        print('')

        # Perfect drying heat demand
        print('Total heat requirement for perfect drying:', heat_drying, 'kJ')
        print('Heat requirement for perfect drying per kg of feedstock:', heat_drying / mass_feedstock, 'kJ/kg')
        print('Heat requirement per kg of water removed:', heat_drying / mass_evaporated_water, 'kJ/kg')
        print('')

        # Imperfect drying heat demand
        print('Total heat requirement for imperfect drying:', heat_drying_post_dryer_efficiency, 'kJ')
        print('Heat requirement for imperfect drying per kg of feedstock:',
              heat_drying_post_dryer_efficiency / mass_feedstock, 'kJ/kg')
        print('Heat requirement for imperfect drying per kg of feedstock:',
              (heat_drying_post_dryer_efficiency / 3600) / mass_feedstock, 'kWh/kg')
        print('Heat requirement per kg of water removed:', heat_drying_post_dryer_efficiency / mass_evaporated_water,
              'kJ/kg')
        print('')

        # Electricity demand
        print('Total electricity requirement:', electricity_drying, 'kWh')
        print('Electricity requirement per kg of feedstock:', electricity_drying / mass_feedstock, 'kWh/kg')
        print('Electricity requirement per kg of feedstock:', (electricity_drying * 3600) / mass_feedstock, 'kJ/kg')
        print('Electricity requirement per kg of water removed:', electricity_drying / mass_evaporated_water, 'kWh/kg')
        print('Electricity requirement per kg of water removed:', (electricity_drying * 3600) / mass_evaporated_water,
              'kJ/kg')
        print('')

        # Drying energy source
        print('Energy source for drying:', energy_source_drying)

    return energies_out


def load_milling_pelleting_data(full_file_path=None):
    """
    Load pickled data done in analysis on milling and pelleting energy demands.
    Analysis done in: analysis/preliminary/milling_pelleting/milling_pelleting_energy_consumption.ipynb.

    Parameters
    ----------
    full_file_path: str
    "r" string specifying the file path to pickle object.

    Returns
    -------
    dict
        Loaded data on milling and pelleting energy demands etc.
    """
    if full_file_path is None:
        project_root = get_project_root()
        full_file_path = str(project_root) + r"\data\milling_pelleting_results"

    # Load pickled data
    loaded_data = pickle.load(open(full_file_path, "rb"))

    return loaded_data


def electricity_milling(screensize=None, feedstock_type=None, show_warnings=True):
    """
    Calculates the electricity requirements for milling 1 tonne of feedstock.
    Analysis and data: analysis/preliminary/milling_pelleting/milling_pelleting_energy_consumption.ipynb.

    Parameters
    ----------
    screensize: None | float
        Defines which size mill screen should be used in process [mm].
    feedstock_type: None | str
        Specifies the type of feedstock
    show_warnings: bool
        Determine whether warnings should be displayed.

    Returns
    -------
    tuple[float, float]
        1st Entry: Electricity requirement for milling [kWh/tonne].
        2nd Entry: Particle size post milling [mm].
    """
    # Load defaults
    if screensize is None:
        screensize = 3.2

    if feedstock_type is None:
        feedstock_type = settings.user_inputs.feedstock.category

    # Load required data
    data = load_milling_pelleting_data()

    # Check input is right dimension
    if screensize > data["Energy milling model"]["X_limits"]["max"] and show_warnings:
        warnings.warn("Screen size larger than reference values.")
    if screensize < data["Energy milling model"]["X_limits"]["min"] and show_warnings:
        warnings.warn("Screen size smaller than reference values")

    # Get energy milling prediction and error
    milling_prediction = data["Energy milling model"]["Regression function"](screensize)  # [kWh/tonne]
    milling_rmse = data["Energy milling model"]["RMSE"]  # [kWh/tonne]

    # Calculate randomised electricity requirement
    electricity_requirement = np.random.normal(milling_prediction, milling_rmse)  # [kWh/tonne]

    # Add energy penalty for woody biomass
    if feedstock_type == "woody biomass":
        electricity_requirement += data["Difference energy requirement milling - herbaceous and woody biomass"]

    # Get particle size prediction and error
    particle_size_prediction = data["Particle size from milling"]["Regression function"](screensize)  # [kWh/tonne]
    particle_size_rmse = data["Particle size from milling"]["RMSE"]  # [kWh/tonne]

    # Calculate randomised particle size post milling
    particle_size = np.random.normal(particle_size_prediction, particle_size_rmse)

    return electricity_requirement, particle_size


def electricity_pelleting(particle_size=None, show_warnings=True):
    """
    Calculates the electricity requirements for pelleting 1 tonne of feedstock.
    Analysis and data: analysis/preliminary/milling_pelleting/milling_pelleting_energy_consumption.ipynb.

    Parameters
    ----------
    particle_size: float
        Particle size of feedstock either as received or after milling.
    show_warnings: bool
        Determine whether warnings should be displayed.

    Returns
    -------
    float
        Electricity requirement for pelleting [kWh/tonne].
    """

    # Get defaults
    if particle_size is None:
        try:
            particle_size = settings.user_inputs.feedstock.particle_size_post_milling
        except:
            particle_size = settings.user_inputs.feedstock.particle_size_ar

    # Run checks
    if particle_size > 31 and show_warnings:
        warnings.warn("Particle size larger than currently supported. Consider adding milling process.")

    # Load required data:
    data = load_milling_pelleting_data()

    # Get energy pelleting prediction and error
    prediction = data["Pelleting model"]["Regression function"](particle_size)  # [kWh/tonne]
    rmse = data["Pelleting model"]["RMSE"]  # [kWh/tonne]

    # Calculate randomised electricity requirement
    electricity_requirement = np.random.normal(prediction, rmse)  # [kWh/tonne]

    return electricity_requirement


def electricity_shredding():
    """
    Calculates the electricity requirements for shredding 1 tonne of baled feedstock to a length of 25 to 100 mm.
    Source: https://doi.org/10.13140/RG.2.2.17486.25922
    Parameters
    ----------

    Returns
    -------
    float
        Electricity requirement for shredding [kWh/tonne].
    """

    # Get electricity requirements - Note reference suggests that substantial savings could be made but also that
    # requirements could increase.
    shredding_electricity_requirement_most_likely = 14.9  # [kWh/tonne]
    shredding_electricity_requirement_lower_estimate = shredding_electricity_requirement_most_likely * 0.5
    shredding_electricity_requirement_upper_estimate = shredding_electricity_requirement_most_likely * 1.5

    # Calculate randomised electricity requirement
    default_generator = np.random.default_rng()  # Initialise default generator
    # Get req in [kWh/tonne]
    electricity_requirement = default_generator.triangular(left=shredding_electricity_requirement_lower_estimate,
                                                           mode=shredding_electricity_requirement_most_likely,
                                                           right=shredding_electricity_requirement_upper_estimate)

    return electricity_requirement
