import numpy as np
from config import settings
import warnings
import random
from functions.general.utility import kJ_to_kWh


def energy_drying(mass_feedstock=settings.general.FU,
                  moisture_ar=settings.user_inputs["as received moisture"],
                  moisture_post_drying=settings.user_inputs["desired moisture"],
                  dryer_type=settings.user_inputs.dryer_type,
                  specific_heat_reference_temp=settings.user_inputs.specific_heat_reference_temp,
                  electricity_reference=settings.user_inputs.electricity_reference,
                  output_unit=settings.user_inputs.drying_output_unit,
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
        warnings.warn("Ensure that moisture contents are given as percentages.", UserWarning)
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
    # TODO: Add auxiliary energy requirements and make sure to add to requirements below and LCA function

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
    if output_unit == "kWh":
        energies_out = {"heat": kJ_to_kWh(heat_drying_post_dryer_efficiency),
                        "electricity": electricity_drying,
                        "heat source": energy_source_drying, "units": output_unit
                        }
    elif output_unit == "kJ":
        energies_out = {"heat": heat_drying_post_dryer_efficiency,
                        "electricity": kJ_to_kWh(electricity_drying, reverse=True),
                        "heat source": energy_source_drying, "units": output_unit
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


# Define models for milling and pelleting process based on analysis in:
# analysis\preliminary\milling_pelleting_energy_consumption_v0.ipynb

def electricity_milling(screensize="3.2"):
    """
    Calculates the electricity requirements for milling 1 tonne of feedstock.
    Original data from: "10.13031/aea.30.9719".

    Parameters
    ----------
    screensize: str
        Defines which size mill screen should be used in process. "3.2" results in a finer mill, whereas "6.5" results
        in a coarser mill.

    Returns
    -------
    float
        (1) Electricity requirement for milling [kWh/tonne].
        (2) Particle size post milling [mm].
    """

    # Define data:
    if screensize == "3.2":
        mean_energy_mill = 33.96  # [kWh/tonne]
        std_energy_mill = 4.09  # [kWh/tonne]
        particle_size = random.uniform(15, 18)  # [mm]
    elif screensize == "6.5":
        mean_energy_mill = 13.81  # [kWh/tonne]
        std_energy_mill = 0.24  # [kWh/tonne]
        particle_size = random.uniform(20, 31)  # [mm]

    else:
        raise ValueError("Wrong milling screensize given.")

    # Calculate randomised electricity requirement
    electricity_requirement = np.random.normal(mean_energy_mill, std_energy_mill)  # [kWh/tonne]

    return electricity_requirement, particle_size


def electricity_pelleting(particle_size=None, show_warnings=True):
    """
    Calculates the electricity requirements for pelleting 1 tonne of feedstock.
    Original data from: "10.13031/aea.30.9719".

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
            particle_size = settings.user_inputs["particle size after milling"]
        except:
            particle_size = settings.user_inputs["particle size"]

    # Define data:
    if particle_size >= 19:
        mean_energy_pelleting = 140.74  # [kWh/tonne]
        std_energy_pelleting = 30.89  # [kWh/tonne]
        if particle_size > 31 and show_warnings:
            warnings.warn("Particle size larger than currently supported. Consider adding milling process.")
    elif particle_size < 19:
        mean_energy_pelleting = 109.92  # [kWh/tonne]
        std_energy_pelleting = 11.90  # [kWh/tonne]
        if particle_size < 15 and show_warnings:
            warnings.warn("Particle size smaller than reference values. Pelleting not typical at this particle size.")
    else:
        raise ValueError("Supplied particle size in the wrong format")

    # Calculate randomised electricity requirement
    electricity_requirement = np.random.normal(mean_energy_pelleting, std_energy_pelleting)  # [kWh/tonne]

    return electricity_requirement
