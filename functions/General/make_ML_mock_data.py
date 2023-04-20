import random
import math

import pandas as pd

from config import settings
from functions.general.utility import get_project_root


# Define helper functions
def load_source_data(data_source=None):
    if data_source is None:
        project_root = get_project_root()
        data_source = str(project_root) + r"\data\20220810_Dataset_Gasification_Ascher_predictors.csv"
    return pd.read_csv(data_source)


def make_mock_data_instance(label, source_data=load_source_data()):
    """
    Function to make mock data instances. Could use other methods such as drawing from distributions etc.
    Parameters
    ----------
    label
    source_data

    Returns
    -------

    """
    value = random.choice(source_data[label])
    if not isinstance(value, str) \
            and not label == "bed_material" \
            and not label == "operating_condition":  # deal with str variable type and bed material
        while math.isnan(value):  # draw until an instance that is no NaN is drawn.
            value = random.choice(source_data[label])
    return value


# Define main function
def make_gasification_mock_data(C=None, H=None, S=None, particle_size=None, ash=None, moisture=None, temperature=None,
                                operating_condition=None, ER=None, catalyst=None, scale=None, agent=None, reactor=None,
                                bed=None, data_index=None):
    """
    Function to create mock data for machine learning gasification prediction model.

    Parameters
    ----------
    C
    H
    S
    particle_size
    ash
    moisture
    temperature
    operating_condition
    ER
    catalyst
    scale
    agent
    reactor
    bed
    data_index: str
        Label to be used to give data a name.

    Returns
    -------
    pandas.DataFrame
        Mock data to test ML prediction model on.
    """

    # Initialise empty data frame to store mock data
    if data_index is None:
        data_index = "mock data"
    input_data_labels = settings.labels.input_data
    mock_data = pd.DataFrame(index=[data_index], columns=input_data_labels)

    # Update feedstock ultimate and proximate analysis data.

    if C is None:
        mock_data.loc[data_index]["C [%daf]"] = make_mock_data_instance("C")
    else:
        mock_data.loc[data_index]["C [%daf]"] = C

    if H is None:
        mock_data.loc[data_index]["H [%daf]"] = make_mock_data_instance("H")
    else:
        mock_data.loc[data_index]["H [%daf]"] = H

    if S is None:
        mock_data.loc[data_index]["S [%daf]"] = make_mock_data_instance("S")
    else:
        mock_data.loc[data_index]["S [%daf]"] = S

    if particle_size is None:
        mock_data.loc[data_index]["Particle size [mm]"] = make_mock_data_instance("feed_particle_size")
    else:
        mock_data.loc[data_index]["Particle size [mm]"] = particle_size

    if ash is None:
        mock_data.loc[data_index]["Ash [%db]"] = make_mock_data_instance("feed_ash")
    else:
        mock_data.loc[data_index]["Ash [%db]"] = ash

    if moisture is None:
        mock_data.loc[data_index]["Moisture [%wb]"] = make_mock_data_instance("feed_moisture")
    else:
        mock_data.loc[data_index]["Moisture [%wb]"] = moisture

    # Update operating conditions.

    if temperature is None:
        mock_data.loc[data_index]["Temperature [°C]"] = make_mock_data_instance("temperature")
    else:
        mock_data.loc[data_index]["Temperature [°C]"] = temperature

    if operating_condition is None:
        operating_condition_value = make_mock_data_instance("operating_condition")
        if not isinstance(operating_condition_value, str) and math.isnan(operating_condition_value):
            operating_condition_value = "continuous"  # fix some missing value instances
    else:
        operating_condition_value = operating_condition

    if operating_condition_value == "batch":
        mock_data.loc[data_index]["Operation (Batch/Continuous)"] = 0
    elif operating_condition_value == "continuous":
        mock_data.loc[data_index]["Operation (Batch/Continuous)"] = 1
    else:
        raise ValueError("Only 'batch' or 'continuous' allowed.")

    if ER is None:
        mock_data.loc[data_index]["ER"] = make_mock_data_instance("ER")
    else:
        mock_data.loc[data_index]["ER"] = ER

    if catalyst is None:
        mock_data.loc[data_index]["Catalyst"] = make_mock_data_instance("catalyst")
    else:
        mock_data.loc[data_index]["Catalyst"] = catalyst

    if scale is None:
        scale_value = make_mock_data_instance("scale")
    else:
        scale_value = scale

    if scale_value == "lab":
        mock_data.loc[data_index]["Scale"] = 0
    elif scale_value == "pilot":
        mock_data.loc[data_index]["Scale"] = 1
    else:
        raise TypeError("Only 'Lab' or 'Pilot' allowed.")

    if agent is None:
        agent_value = make_mock_data_instance("gasifying_agent")
    else:
        agent_value = agent

    if agent_value == "air":
        mock_data.loc["mock data"]["Agent_air":"Agent_steam"] = [1, 0, 0, 0, 0]
    elif agent_value == "air + steam":
        mock_data.loc["mock data"]["Agent_air":"Agent_steam"] = [0, 1, 0, 0, 0]
    elif agent_value == "other":
        mock_data.loc["mock data"]["Agent_air":"Agent_steam"] = [0, 0, 1, 0, 0]
    elif agent_value == "oxygen":
        mock_data.loc["mock data"]["Agent_air":"Agent_steam"] = [0, 0, 0, 1, 0]
    elif agent_value == "steam":
        mock_data.loc["mock data"]["Agent_air":"Agent_steam"] = [0, 0, 0, 0, 1]
    else:
        raise TypeError('Only "air" OR "air + steam" OR "other" OR "oxygen" OR "steam" allowed.')

    if reactor is None:
        reactor_value = make_mock_data_instance("reactor_type")
    else:
        reactor_value = reactor

    if reactor_value == "fixed bed":
        mock_data.loc["mock data"]["Reactor_fixed bed":"Reactor_other"] = [1, 0, 0]
    elif reactor_value == "fluidised bed":
        mock_data.loc["mock data"]["Reactor_fixed bed":"Reactor_other"] = [0, 1, 0]
    elif reactor_value == "other":
        mock_data.loc["mock data"]["Reactor_fixed bed":"Reactor_other"] = [0, 0, 1]
    else:
        raise TypeError('Only "fixed" OR "fluidised" OR "other" allowed')

    if bed is None:
        bed_value = make_mock_data_instance("bed_material")

        if mock_data.loc["mock data"]["Reactor_fluidised bed"] != 1:  # overwrite value to N/A if not fluidised bed
            bed_value = "N/A"
    else:
        bed_value = bed

    if bed_value == "N/A":
        mock_data.loc["mock data"]["Bed_N/A":"Bed_silica"] = [1, 0, 0, 0, 0]
    elif agent_value == "alumina":
        mock_data.loc["mock data"]["Bed_N/A":"Bed_silica"] = [0, 1, 0, 0, 0]
    elif agent_value == "olivine":
        mock_data.loc["mock data"]["Bed_N/A":"Bed_silica"] = [0, 0, 1, 0, 0]
    elif agent_value == "silica":
        mock_data.loc["mock data"]["Bed_N/A":"Bed_silica"] = [0, 0, 0, 0, 1]
    else:
        mock_data.loc["mock data"]["Bed_N/A":"Bed_silica"] = [0, 0, 0, 1, 0]

    return mock_data
