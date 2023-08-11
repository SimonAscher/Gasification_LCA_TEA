import io
import os
import pathlib
import zipfile
import streamlit as st

from dynaconf import Dynaconf
from matplotlib import pyplot as plt
from objects import Results
from functions.general.utility import get_project_root
from config import settings

def display_correct_user_distribution_inputs(choice, key):
    """
    Displays the correct input fields based on the user's selected distribution type.

    Parameters
    ----------
    choice: str
        Chosen distribution type.
    key: str
        Key identifying what the distribution choices are shown for. This avoids DuplicateWidgetID error.

    Returns
    -------
    dict
        Given user inputs.
    """
    dist_values = None
    if choice == "fixed":
        value = st.number_input(label="Constant value", key=key + "fixed constant")
        dist_values = {"value": value, "distribution_type": choice}

    elif choice == "range":
        low = st.number_input(label="Distribution lower bound", key=key + "range low")
        high = st.number_input(label="Distribution upper bound", key=key + "range high")
        dist_values = {"low": low, "high": high, "distribution_type": choice}

    elif choice == "triangular":
        lower = st.number_input(label=" Distribution lower bound", key=key + "triangular lower")
        mode = st.number_input(label="Distribution mode", key=key + "triangular mode")
        upper = st.number_input(label="Distribution upper bound", key=key + "triangular upper")
        dist_values = {"lower": lower, "mode": mode, "upper": upper, "distribution_type": choice}

    elif choice == "gaussian":
        mean = st.number_input(label="Distribution mean", key=key + "gaussian mean")
        std = st.number_input(label="Distribution standard deviation (σ)", key=key + "gaussian standard deviation")
        dist_values = {"mean": mean, "std": std, "distribution_type": choice}

    return dist_values


def save_uploaded_user_inputs_to_toml(uploaded_user_input_file):
    """
    RETIRED METHOD
    Takes the user input data and writes it to a temporary file/path.

    Notes
    -----
    Care has to be taken to delete the temporary path after use. For this use: os.remove(complete_path)

    Parameters
    ----------
    uploaded_user_input_file: UploadedFile
        User input .toml file uploaded by user.

    Returns
    -------

    """
    # Get path
    data = uploaded_user_input_file.getvalue().decode('utf-8')
    parent_path = pathlib.Path(__file__).parent.resolve()
    save_path = os.path.join(parent_path, "user_inputs")
    complete_path = os.path.join(save_path, uploaded_user_input_file.name)

    with open(complete_path, "w") as destination_file:  # write data to user input file
        destination_file.write(data)

    return complete_path


def update_settings_with_user_inputs(uploaded_user_input_file, reset_sensitivity_analysis=True):
    """
    Takes the uploaded user input data and updates Dynaconf settings with it.

    Parameters
    ----------
    uploaded_user_input_file: UploadedFile
        User input .toml file uploaded by user.
    reset_sensitivity_analysis: bool
        Determines whether sensitivity analysis values should be reset.

    Returns
    -------

    """
    #TODO: Could change this method and the method below to just directly create a dictionary which is then used to
    # update settings instead of writing to a temporary file.

    # Get path
    data = uploaded_user_input_file.getvalue().decode('utf-8')
    parent_path = pathlib.Path(__file__).parent.resolve()
    save_path = os.path.join(parent_path, "temp")
    user_inputs_path = os.path.join(save_path, uploaded_user_input_file.name)

    with open(user_inputs_path, "w") as destination_file:  # write data to user input file
        destination_file.write(data)

    root_path = get_project_root()

    # Get settings
    if reset_sensitivity_analysis:
        files_to_update = [user_inputs_path,  # user inputs (overwrites defaults)
                           root_path + r"\configs\sensitivity_analysis_defaults.toml"  # reverts to default sensitivity analysis choices
                           ]
    else:
        files_to_update = [user_inputs_path]

    settings_updated = Dynaconf(
        settings_files=files_to_update,
        environments=True,  # Enable layered environments
        merge_enabled=True  # Allows for default inputs to be overwritten
    )

    # update settings with file selected by user and remove temporary file
    settings.update(settings_updated)
    os.remove(user_inputs_path)


def update_settings_with_sensitivity_analysis_choices(uploaded_sensitivity_analysis_choices_file):
    """
    Takes the uploaded sensitivity analysis data and updates Dynaconf settings with it.

    Parameters
    ----------
    uploaded_sensitivity_analysis_choices_file: UploadedFile
        Sensitivity analysis .toml file uploaded by user.

    Returns
    -------

    """
    # Get path
    data = uploaded_sensitivity_analysis_choices_file.getvalue().decode('utf-8')
    parent_path = pathlib.Path(__file__).parent.resolve()
    save_path = os.path.join(parent_path, "temp")
    sensitivity_analysis_path = os.path.join(save_path, uploaded_sensitivity_analysis_choices_file.name)

    with open(sensitivity_analysis_path, "w") as destination_file:  # write data to user input file
        destination_file.write(data)

    # Get settings
    settings_updated = Dynaconf(
        settings_files=[  # Paths to toml files
            sensitivity_analysis_path
        ],
        environments=True,  # Enable layered environments
        merge_enabled=True  # Allows for default inputs to be overwritten
    )

    # update settings with file selected by user and remove temporary file
    settings.update(settings_updated)
    os.remove(sensitivity_analysis_path)
    # TODO: Update to use temporary directory and not os.remove method.


def show_simulation_results(results):
    """
    Display formatted figures for supplied results.

    Parameters
    ----------
    results: Results

    Returns
    -------

    """
    st.header("Simulation results")

    # LCA plots
    with st.expander("Environmental Analysis (Life Cycle Assessment) Results"):
        st.subheader("Global Global Warming Potential")
        st.pyplot(results.figures["global_GWP"])
        st.subheader("Global Warming Potential by Process")
        st.pyplot(results.figures["global_GWP_byprocess"])
        st.subheader("Average Global Warming Potential by Process")
        st.pyplot(results.figures["average_GWP_byprocess"])

    # Energy generation plots
    with st.expander("Energy Generation Performance of System"):
        st.subheader("Net Energy Generation Performance of the System")
        st.pyplot(results.figures["energy_global"])
        st.subheader("Electricity Generation and Consumption by Process")
        st.pyplot(results.figures["energy_electricity"])
        st.subheader("Heat Generation and Consumption by Process")
        st.pyplot(results.figures["energy_heat"])

def download_zipped_figures(results, figure_file_type=None):
    """
    Arranges figures in .zip and allows user to download them.

    results: Results

    Parameters
    ----------

    Returns
    -------

    """
    st.subheader("Download created figures")
    if figure_file_type is None:
        figure_file_type = ".png"

    # TODO: Could implement this as an alternative but would need to figure out how to stop app from rerunning with
    #  session state
    # figure_file_type = st.selectbox(label="Select your desired figure file type",
    #                                 options=[".png", ".jpg", ".pdf", ".tiff"])

    zip_file_name = results.ID + ".zip"

    # Write figures to zip file
    with zipfile.ZipFile(zip_file_name, mode="w") as z:
        for item in results.figures.items():
            file_name = item[0] + figure_file_type
            figure = item[1]
            buf = io.BytesIO()
            figure.savefig(buf)
            plt.close()
            z.writestr(file_name, buf.getvalue())

    # Show download button for user to download zipped figures.
    with open(zip_file_name, "rb") as zip_file:
        st.download_button(
            label="Download .zip",
            data=zip_file,
            file_name="export.zip",
            mime="application/zip"
        )
    os.remove(zip_file_name)
    # TODO: Update to use temporary directory and not os.remove method.


def sensitivity_analysis_energy_impact(widget_output, baseline_emissions, energy_type):
    """
    Returns correct energy impact based on energy type and widget output.

    Parameters
    ----------
    widget_output: str
        Widget output selected by user.
    baseline_emissions: float
        Baseline emissions of energy type.
    energy_type: str
        String representing the energy type (i.e. "Heat" or "Electricity")

    Returns
    -------

    """
    if widget_output == "default":
        energy_impact_value = None
    elif widget_output == "75 % of current emissions":
        energy_impact_value = baseline_emissions * 0.75

    elif widget_output == "50 % of current emissions":
        energy_impact_value = baseline_emissions * 0.50

    elif widget_output == "25 % of current emissions":
        energy_impact_value = baseline_emissions * 0.25

    elif widget_output == "user defined":
        energy_impact_value = st.number_input(label=f"{energy_type} impact [kg CO2eq./kWh]")
    else:
        raise ValueError("Option not defined.")

    if energy_impact_value is not None:
        st.write(f"Updated {energy_type} impact of {energy_impact_value:.3f} [kg CO2eq./kWh] will be used in "
                 f"sensitivity analysis.")

    return energy_impact_value
