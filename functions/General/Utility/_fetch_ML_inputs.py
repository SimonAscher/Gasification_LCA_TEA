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

    # Get sub lists

    # Elementary composition
    elementary_composition = [settings_location["carbon content"], settings_location["hydrogen content"],
                              settings_location["sulphur content"]]

    # Proximate composition and particle size

    # Check if pelleting or milling have been selected. Order of priority: Pelleting -> Milling -> Default
    try:
        particle_size = settings_location["particle size after pelleting"]
    except:
        try:
            particle_size = settings_location["particle size after milling"]
        except:
            particle_size = settings.user_inputs["particle size"]

    proximate_and_PS = [particle_size, settings_location["ash content"],
                        settings_location["desired moisture"]]

    # Operating conditions
    temperature = settings_location["temperature"]

    # Operation mode
    if settings_location["operation mode"] == "Batch":
        operation = 0
    elif settings_location["operation mode"] == "Continuous":
        operation = 1
    else:
        raise TypeError("Only 'Batch' or 'Continuous' allowed.")

    # Equivalence ratio
    ER = settings_location["ER"]

    # Catalyst use
    if not settings_location["catalyst"]:
        catalyst = 0
    elif settings_location["catalyst"]:
        catalyst = 1
    else:
        raise TypeError("Only 'true' or 'false' allowed.")

    # System scale
    if settings_location["operation scale"] == "Lab":
        scale = 0
    elif settings_location["operation scale"] == "Pilot":
        scale = 1
    else:
        raise TypeError("Only 'Lab' or 'Pilot' allowed.")

    # Collect single values in list
    operating_conditions = [temperature, operation, ER, catalyst, scale]
    # TODO: Double check that all one hot encoded arrays below are in right order for the right variable
    # Gasifying agent
    if settings_location["gasifying agent"] == "Air":
        agent = [1, 0, 0, 0, 0]
    elif settings_location["gasifying agent"] == "Air + steam":
        agent = [0, 1, 0, 0, 0]
    elif settings_location["gasifying agent"] == "Other":
        agent = [0, 0, 1, 0, 0]
    elif settings_location["gasifying agent"] == "Oxygen":
        agent = [0, 0, 0, 1, 0]
    elif settings_location["gasifying agent"] == "Steam":
        agent = [0, 0, 0, 0, 1]
    else:
        raise TypeError('Only "Air" OR "Air + steam" OR "Other" OR "Oxygen" OR "Steam" allowed.')

    # Reactor type
    if settings_location["reactor type"] == "Fixed":
        reactor = [1, 0, 0]
    elif settings_location["reactor type"] == "Fluidised":
        reactor = [0, 1, 0]
    elif settings_location["reactor type"] == "Other":
        reactor = [0, 0, 1]
    else:
        raise TypeError('Only "Fixed" OR "Fluidised" OR "Other" allowed.')

    # Gasifier bed material
    if settings_location["bed material"] == "N/A":
        bed = [1, 0, 0, 0, 0]
    elif settings_location["bed material"] == "Alumina":
        bed = [0, 1, 0, 0, 0]
    elif settings_location["bed material"] == "Olivine":
        bed = [0, 0, 1, 0, 0]
    elif settings_location["bed material"] == "Other":
        bed = [0, 0, 0, 1, 0]
    elif settings_location["bed material"] == "Silica":
        bed = [0, 0, 0, 0, 1]
    else:
        raise TypeError('Only "N/A" OR "Alumina" OR "Olivine" OR "Other" OR "Silica" allowed.')

    # Combine all lists
    data = elementary_composition + proximate_and_PS + operating_conditions + agent + reactor + bed

    return data
