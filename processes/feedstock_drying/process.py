from config import settings

user_inputs = settings.user_inputs.drying_process


def energy_drying(mass_feedstock, moisture_ar, moisture_post_drying,
                  dryer_type=user_inputs.dryer_type,
                  specific_heat_reference_temp=user_inputs.specific_heat_reference_temp,
                  electricity_reference=user_inputs.electricity_reference, output_unit=user_inputs.output_unit,
                  syngas_as_fuel=False, show_values=False):
    """
    Function used to calculate the energy requirements to dry a feedstock.

    Parameters
    ----------
    mass_feedstock: float
        Initial feedstock mass on an as received basis [kg].
    moisture_ar: float
        Moisture content of feedstock before drying (i.e. as received basis) as a decimal.
    moisture_post_drying: float
        Desired moisture content of feedstock after drying as a decimal.
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
    dict
        Dictionary of energy requirements in the form of heat and electricity including their sources and the units.
        Note: Heat requirement given as amount of raw heat source required (e.g. XYZ kWh of natural gas)
    -------

    """
    # TODO: Add defaults for first 3 variables - i.e. FU, and user inputs for moisture AR and desired

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

    if moisture_ar < moisture_post_drying:  # check for erroneous inputs
        raise ValueError("Warning: Moisture content of as received feedstock must be higher than moisture content "
                         "post drying.")

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
    if output_unit == "kWh":
        energies_out = {"heat": heat_drying_post_dryer_efficiency / 3600, "electricity": electricity_drying,
                        "heat source": energy_source_drying, "units": output_unit}
    elif output_unit == "kJ":
        energies_out = {"heat": heat_drying_post_dryer_efficiency, "electricity": electricity_drying * 3600,
                        "heat source": energy_source_drying, "units": output_unit}

    # Print calculations if desired
    if show_values:
        # Evaporated water calculations:
        print('Mass of initial feedstock:', mass_feedstock, '[kg]')
        print('Mass of water in intial feedstock:', mass_water_initial, '[kg]')
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


def drying_GWP(energy_drying_dict):
    """
    Calculates the GWP due to energy demand for drying.

    Parameters
    ----------
    energy_drying_dict: dict
        Output from energy_drying function containing heat and electricity requirements and units and heat source.

    Returns
    -------

    """
    # Convert units to kWh if not given in kWh already
    if energy_drying_dict["units"] == "kJ":
        energy_drying_dict["heat"] = energy_drying_dict["heat"] / 3600
        energy_drying_dict["electricity"] = energy_drying_dict["electricity"] / 3600
        energy_drying_dict["units"] = "kWh"

    # Calculate impact due to electricity usage (Note: counterbalanced by avoided electricity usage due to scheme)
    electricity_CO2_eq = settings.data.CO2_equivalents.electricity[settings.user_inputs.country]
    electricity_GWP = energy_drying_dict["electricity"]

    from functions.LCA.helpers import natural_gas_for_heat_GWP

    # Calculate impact due to heat demands
    if energy_drying_dict["heat source"] == "natural gas":
        heat_GWP = natural_gas_for_heat_GWP(energy_drying_dict["heat"], energy_drying_dict["units"])

    # Sum GWPs
    total_GWP = electricity_GWP + heat_GWP

    return total_GWP
