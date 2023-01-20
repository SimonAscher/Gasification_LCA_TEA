from config import settings


def calculate_syngas_LHV(predictions, units="MJ/m3"):
    """
    Calculates syngas LHV from ML predictions.

    Parameters
    ----------
    predictions: dict
        ML predictions on gasification outputs.
    units: str
        Defines in what units data is to be returned ("MJ/m3" or "MJ/kg").
    Returns
    -------
    dict
        Syngas LHV [MJ/m3] or Syngas LHV [MJ/kg].
    """
    # Extract gas fractions
    H2 = predictions["H2 [vol.% db]"] / 100
    CO = predictions["CO [vol.% db]"] / 100
    CH4 = predictions["CH4 [vol.% db]"] / 100
    C2Hn = predictions["C2Hn [vol.% db]"] / 100

    LHV = (H2 * settings.data.LHV.H2 + CO * settings.data.LHV.CO + CH4 * settings.data.LHV.CH4 +
           C2Hn * settings.data.LHV.C2H4)  # [MJ/m3]

    if units == "MJ/m3":
        output = {"Calculated LHV": LHV, "ML predicted LHV": predictions["LHV [MJ/Nm3]"], "Units": "[MJ/m3]"}

    elif units == "MJ/kg":
        # Extract other required gas fractions
        N2 = predictions["N2 [vol.% db]"] / 100
        CO2 = predictions["CO2 [vol.% db]"] / 100

        syngas_density = (N2 * settings.data.densities.N2 + H2 * settings.data.densities.H2 +
                          CO * settings.data.densities.CO + CO2 * settings.data.densities.CO2 +
                          CH4 * settings.data.densities.CH4 + C2Hn * settings.data.densities.C2H4)  # [kg/m3]

        output = {"Calculated LHV": LHV * (1 / syngas_density),
                  "ML predicted LHV": predictions["LHV [MJ/Nm3]"] * (1 / syngas_density),
                  "Units": "[MJ/kg]"}

    else:
        raise ValueError("Invalid units given.")

    return output


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
        The estimated LHV or HHV of a feedstock.
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


def calculate_cold_gas_efficiency(syngas_LHV, syngas_yield, feedstock_LHV):
    """
    Calculate cold gas efficiency (CGE) of gasification process.

    Parameters
    ----------
    syngas_LHV: float
        Syngas LHV [MJ/m3].
    syngas_yield: float
        Syngas yield [m3/kg feedstock].
    feedstock_LHV: float
        Feedstock LHV [MJ/kg feedstock].
    Returns
    -------
    float
        Cold gas efficiency (CGE) of gasification process.
    """
    CGE = (syngas_LHV * syngas_yield) / feedstock_LHV

    return CGE


def calculate_carbon_conversion_efficiency(predictor_data, predictions):
    """
    Calculate carbon conversion efficiency (CCE) of gasification process.

    Parameters
    ----------
    predictor_data: pandas.DataFrame
        Input data to the ML prediction model containing ultimate composition and feedstock moisture data.

    predictions: dict
        ML predictions on gasification outputs.

    Returns
    -------
    float
        Carbon conversion efficiency (CCE) of gasification process.
    """

    # Extract gas fractions
    syngas_CO = predictions["CO [vol.% db]"] / 100
    syngas_CO2 = predictions["CO2 [vol.% db]"] / 100
    syngas_CH4 = predictions["CH4 [vol.% db]"] / 100
    syngas_C2Hn = predictions["C2Hn [vol.% db]"] / 100
    syngas_yield = predictions["Gas yield [Nm3/kg wb]"]

    # Extract feedstock data
    feedstock_C = predictor_data["C [%daf]"] / 100
    feedstock_moisture = predictor_data["Moisture [%wb]"] / 100

    # Extract molar masses
    mmC = settings.data.molar_masses.C
    mmO = settings.data.molar_masses.O
    mmH = settings.data.molar_masses.H

    # Calculations
    carbon_feedstock = float(feedstock_C * (1 / (1 + feedstock_moisture)))  # kg C/ kg feedstock

    carbon_syngas = float((syngas_CO * settings.data.densities.CO * (mmC / (mmC + mmO)) +
                           syngas_CO2 * settings.data.densities.CO2 * (mmC / (mmC + 2 * mmO)) +
                           syngas_CH4 * settings.data.densities.CH4 * (mmC / (mmC + 4 * mmH)) +
                           syngas_C2Hn * settings.data.densities.C2H4 * (2 * mmC / (2 * mmC + 4 * mmH))) *
                          syngas_yield)  # kg C/ kg feedstock

    CCE = (carbon_syngas / carbon_feedstock) * 100  # kg C/ kg feedstock

    return CCE
