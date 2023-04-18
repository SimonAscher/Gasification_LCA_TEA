import warnings

from config import settings


def fetch_ML_inputs():
    """
    Fetches user inputs and gets them in right format for prediction models.

    Returns
    -------
    list
        List of length 24 with elements in required order for prediction model.

    """
    # Define where settings are stored
    settings_location = settings.user_inputs
    feedstock_location = settings_location.feedstock
    process_conditions_location = settings_location.process_conditions
    # Get sub lists

    # Elementary composition
    elementary_composition = [feedstock_location.carbon, feedstock_location.hydrogen,
                              feedstock_location.sulphur]

    # Proximate composition and particle size

    # Check if pelleting or milling have been selected. Order of priority: Pelleting -> Milling -> Default

    if settings_location.processes.milling.included or settings_location.processes.pelleting.included:

        try:
            particle_size = feedstock_location.particle_size_post_pelleting
        except:
            try:
                particle_size = feedstock_location.particle_size_post_milling
            except:
                particle_size = feedstock_location.particle_size_ar
                # warnings.warn("Expected to find particle size post milling or pelleting but could not be found.")
    else:
        particle_size = feedstock_location.particle_size_ar

    if settings_location.processes.drying.included:
        try:
            moisture = feedstock_location.moisture_post_drying
        except:
            moisture = feedstock_location.moisture_ar
            # warnings.warn("Expected to find feedstock moisture post drying but could not be found.")

    else:
        moisture = feedstock_location.moisture_ar

    proximate_and_PS = [particle_size, feedstock_location.ash, moisture]

    # Operating conditions
    temperature = process_conditions_location.gasification_temperature

    # Operation mode
    if process_conditions_location.operation_mode == "Batch":
        operation = 0
    elif process_conditions_location.operation_mode == "Continuous":
        operation = 1
    else:
        raise TypeError("Only 'Batch' or 'Continuous' allowed.")

    # Equivalence ratio
    ER = process_conditions_location.ER

    # Catalyst use
    if not process_conditions_location.catalyst:
        catalyst = 0
    elif process_conditions_location.catalyst:
        catalyst = 1
    else:
        raise TypeError("Only 'true' or 'false' allowed.")

    # System scale
    if process_conditions_location.operation_scale == "Lab":
        scale = 0
    elif process_conditions_location.operation_scale == "Pilot":
        scale = 1
    else:
        raise TypeError("Only 'Lab' or 'Pilot' allowed.")

    # Collect single values in list
    operating_conditions = [temperature, operation, ER, catalyst, scale]
    # TODO: Double check that all one hot encoded arrays below are in right order for the right variable
    # Gasifying agent
    if process_conditions_location.gasifying_agent == "Air":
        agent = [1, 0, 0, 0, 0]
    elif process_conditions_location.gasifying_agent == "Air + steam":
        agent = [0, 1, 0, 0, 0]
    elif process_conditions_location.gasifying_agent == "Other":
        agent = [0, 0, 1, 0, 0]
    elif process_conditions_location.gasifying_agent == "Oxygen":
        agent = [0, 0, 0, 1, 0]
    elif process_conditions_location.gasifying_agent == "Steam":
        agent = [0, 0, 0, 0, 1]
    else:
        raise TypeError('Only "Air" OR "Air + steam" OR "Other" OR "Oxygen" OR "Steam" allowed.')

    # Reactor type
    if process_conditions_location.reactor_type == "Fixed bed":
        reactor = [1, 0, 0]
    elif process_conditions_location.reactor_type == "Fluidised bed":
        reactor = [0, 1, 0]
    elif process_conditions_location.reactor_type == "Other":
        reactor = [0, 0, 1]
    else:
        raise TypeError('Only "Fixed" OR "Fluidised" OR "Other" allowed.')

    # Gasifier bed material
    if process_conditions_location.bed_material == "N/A":
        bed = [1, 0, 0, 0, 0]
    elif process_conditions_location.bed_material == "Alumina":
        bed = [0, 1, 0, 0, 0]
    elif process_conditions_location.bed_material == "Olivine":
        bed = [0, 0, 1, 0, 0]
    elif process_conditions_location.bed_material == "Other":
        bed = [0, 0, 0, 1, 0]
    elif process_conditions_location.bed_material == "Silica":
        bed = [0, 0, 0, 0, 1]
    else:
        raise TypeError('Only "N/A" OR "Alumina" OR "Olivine" OR "Other" OR "Silica" allowed.')

    # Combine all lists
    data = elementary_composition + proximate_and_PS + operating_conditions + agent + reactor + bed

    return data
