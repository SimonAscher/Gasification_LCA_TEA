from config import settings


def calculate_LHV_HHV_feedstock(predictor_data, heating_value_choice="LHV"):
    """
    Estimates the LHV or HHV of a feedstock based on its ultimate composition (and moisture content).

    HHV model source: https://doi.org/10.1063/5.0059376

    Parameters
    ----------
    predictor_data: pandas.DataFrame
        Input data to the ML prediction model containing ultimate composition and feedstock moisture data.
    heating_value_choice: str
        Determines whether the feedstock's heating value should be returned as "LHV" or "HHV".
    Returns
    -------
    float
        The estimated LHV or HHV of a feedstock [MJ/kg wb].
    """
    # Extract ultimate analysis data
    C = predictor_data["C [%daf]"]
    H = predictor_data["H [%daf]"]
    S = predictor_data["S [%daf]"]
    O = 100 - (C + H + S)  # calculate oxygen by difference

    HHV = 2.8799 + 0.2965 * C + 0.4826 * H - 0.0187 * O

    if heating_value_choice == "LHV":
        moisture = predictor_data["Moisture [%wb]"]
        LHV = HHV - (9 * (H / 100 * (100 / (100 - moisture))) * (
                settings.data.heats_vaporisation.water["18 degC"] / 1000))

        output = float(LHV)

    elif heating_value_choice == "HHV":
        output = float(HHV)

    else:
        raise ValueError("Invalid heating value type.")

    return output