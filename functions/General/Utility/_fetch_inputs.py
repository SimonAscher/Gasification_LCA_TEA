from config import settings


def fetch_ML_inputs():
    """
    Fetches user inputs and gets them in right format for prediction models.

    Returns
    -------
    list
        List of length 24 with elements in required order for prediction model.

    """
    # Get sub lists

    # Elementary composition
    elementary_composition = [settings.user_inputs.prediction_model["C"], settings.user_inputs.prediction_model["H"],
                              settings.user_inputs.prediction_model["S"]]

    # Proximate composition and particle size
    proximate_and_PS = [settings.user_inputs.prediction_model["PS"], settings.user_inputs.prediction_model["Ash"],
                        settings.user_inputs.prediction_model["Moisture post drying"]]

    # Operating conditions
    temperature = settings.user_inputs.prediction_model["T"]

    # Operation mode
    if settings.user_inputs.prediction_model["Operation"] == "Batch":
        operation = 0
    elif settings.user_inputs.prediction_model["Operation"] == "Continuous":
        operation = 1
    else:
        raise TypeError("Only 'Batch' or 'Continuous' allowed.")

    # Equivalence ratio
    ER = settings.user_inputs.prediction_model["ER"]

    # Catalyst use
    if not settings.user_inputs.prediction_model["Catalyst"]:
        catalyst = 0
    elif settings.user_inputs.prediction_model["Catalyst"]:
        catalyst = 1
    else:
        raise TypeError("Only 'true' or 'false' allowed.")

    # System scale
    if settings.user_inputs.prediction_model["Scale"] == "Lab":
        scale = 0
    elif settings.user_inputs.prediction_model["Scale"] == "Pilot":
        scale = 1
    else:
        raise TypeError("Only 'Lab' or 'Pilot' allowed.")

    # Collect single values in list
    operating_conditions = [temperature, operation, ER, catalyst, scale]
    # TODO: Double check that all one hot encoded arrays below are in right order for the right variable
    # Gasifying agent
    if settings.user_inputs.prediction_model["Agent"] == "Air":
        agent = [1, 0, 0, 0, 0]
    elif settings.user_inputs.prediction_model["Agent"] == "Air + steam":
        agent = [0, 1, 0, 0, 0]
    elif settings.user_inputs.prediction_model["Agent"] == "Other":
        agent = [0, 0, 1, 0, 0]
    elif settings.user_inputs.prediction_model["Agent"] == "Oxygen":
        agent = [0, 0, 0, 1, 0]
    elif settings.user_inputs.prediction_model["Agent"] == "Steam":
        agent = [0, 0, 0, 0, 1]
    else:
        raise TypeError('Only "Air" OR "Air + steam" OR "Other" OR "Oxygen" OR "Steam" allowed.')

    # Reactor type
    if settings.user_inputs.prediction_model["Reactor"] == "Fixed":
        reactor = [1, 0, 0]
    elif settings.user_inputs.prediction_model["Reactor"] == "Fluidised":
        reactor = [0, 1, 0]
    elif settings.user_inputs.prediction_model["Reactor"] == "Other":
        reactor = [0, 0, 1]
    else:
        raise TypeError('Only "Fixed" OR "Fluidised" OR "Other" allowed.')

    # Gasifier bed material
    if settings.user_inputs.prediction_model["Bed"] == "N/A":
        bed = [1, 0, 0, 0, 0]
    elif settings.user_inputs.prediction_model["Bed"] == "Alumina":
        bed = [0, 1, 0, 0, 0]
    elif settings.user_inputs.prediction_model["Bed"] == "Olivine":
        bed = [0, 0, 1, 0, 0]
    elif settings.user_inputs.prediction_model["Bed"] == "Other":
        bed = [0, 0, 0, 1, 0]
    elif settings.user_inputs.prediction_model["Bed"] == "Silica":
        bed = [0, 0, 0, 0, 1]
    else:
        raise TypeError('Only "N/A" OR "Alumina" OR "Olivine" OR "Other" OR "Silica" allowed.')

    # Combine all lists
    data = elementary_composition + proximate_and_PS + operating_conditions + agent + reactor + bed

    return data
