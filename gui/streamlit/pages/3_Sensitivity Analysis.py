import sys

from pathlib import Path

from functions.MonteCarloSimulation import run_simulation

# Add root directory
root_path = str(Path(__file__).parent.parent.parent.parent)
sys.path.append(root_path)
# Note: Have all module imports after this

import toml
import streamlit as st

from human_id import generate_id
from config import settings
from functions.gui.streamlit_helpers import update_settings_with_user_inputs, sensitivity_analysis_energy_impact, \
    update_settings_with_sensitivity_analysis_choices, show_simulation_results, download_zipped_figures

# Background data
energy_options = settings.streamlit.sensitivity_analysis_energy_options
sensitivity_analysis_run_options = settings.streamlit.sensitivity_analysis_run_options

# %% Ask user to upload toml file defining baseline scenario.
uploaded_baseline_file = st.file_uploader(label="Upload your baseline user inputs file created in the 'Simulation Inputs' section",
                                          type="toml")

if uploaded_baseline_file is not None:  # Continue with script once a file has been uploaded
    update_settings_with_user_inputs(uploaded_baseline_file)  # Update settings with uploaded user inputs

    # %% Run sensitivity analysis
    st.header("Run sensitivity analysis")

    run_sensitivity_analysis_choice = st.selectbox(label='Choose whether sensitivity analysis should be run from a previously created .toml file or if you want to select the parameters now.',
                                                   options=sensitivity_analysis_run_options, index=0)

    if run_sensitivity_analysis_choice == sensitivity_analysis_run_options[0]:  # Run from uploaded .toml file
        uploaded_sensitivity_analysis_file = st.file_uploader(
            label="Upload .toml file defining previous sensitivity analysis choices",
            type="toml")
        if uploaded_sensitivity_analysis_file is not None:
            update_settings_with_sensitivity_analysis_choices(uploaded_sensitivity_analysis_file)

            # Execute simulation upon button press
            run_simulation_button_bool = st.button("Run simulation")
            if run_simulation_button_bool:
                # Run simulation
                # with st.spinner(text="Running environmental and economic simulation. This may take ~60 seconds."):
                results = run_simulation()
                st.success("Simulation completed")
                show_simulation_results(results)

    else:  # Run from selected inputs
        # %% Start of main sensitivity analysis input section
        st.header("Sensitivity analysis options")

        # Electricity impact
        st.subheader("Alternative electricity impact")

        # Get relevant background data
        country = settings.user_inputs.general.country
        electricity_source = settings.user_inputs.reference_energy_sources.electricity
        electricity_baseline_emissions = settings.data.CO2_equivalents.electricity[country]

        # Create widget
        st.write(f"Baseline {electricity_source} emissions of {country} based on the current {electricity_source} mix "
                 f"are {electricity_baseline_emissions} [kg CO2eq./kWh]")
        electricity_sensitivity_choice = st.radio(label="Electricity sensitivity analysis options",
                                                  options=energy_options,
                                                  index=0)

        electricity_impact_value = sensitivity_analysis_energy_impact(electricity_sensitivity_choice,
                                                                      electricity_baseline_emissions,
                                                                      "Electricity")

        st.markdown("""---""")

        # Heat impact
        st.subheader("Alternative heat/thermal energy impact")

        # Get relevant background data
        heat_source = settings.user_inputs.reference_energy_sources.heat
        if heat_source == "natural gas":
            heat_baseline_emissions = settings.data.CO2_equivalents.thermal_energy.natural_gas[country]
        else:
            raise ValueError("This heat source is not yet supported.")

        # Create widget
        st.write(f"The baseline heat source for {country} is {heat_source}. "
                 f"This has an impact of {heat_baseline_emissions} [kg CO2eq./kWh]")

        heat_sensitivity_choice = st.radio(label="Heat sensitivity analysis options", options=energy_options,
                                           index=0)

        heat_impact_value = sensitivity_analysis_energy_impact(heat_sensitivity_choice, heat_baseline_emissions, "Heat")

        st.markdown("""---""")

        # %% Compile sensitivity analysis user choices

        # Create inner dict without "default" parameter - can be used to directly update settings.
        sensitivity_analysis_choices_inner_dict = {
            "sensitivity_analysis": {
                "energy_impacts": {"electricity": electricity_impact_value,
                                   "heat": heat_impact_value}
            }
        }

        # %% Let user download choices if desired
        st.subheader("Compile sensitivity analysis choices and download (optional)")
        if st.button(label='Compile sensitivity analysis choices',
                     help="This is optional, but may be helpful if the selected choices want to be saved for a later run."):
            # Generate file name and store choices in dict
            ID = generate_id()
            sensitivity_analysis_file_name = "sensitivity_analysis_choices_" + ID + ".toml"

            # Create dict with "default" parameter - can be used to save dictionary to .toml file
            sensitivity_analysis_choices_dict_w_default = {"default": sensitivity_analysis_choices_inner_dict}

            st.success("Data successfully compiled. Download below.")

            # Serialize the dictionary to a string using TOML
            toml_data = toml.dumps(sensitivity_analysis_choices_dict_w_default).encode('utf-8')

            # Create a download button that allows the user to download the TOML file
            st.download_button(label='Download sensitivity analysis choices', data=toml_data,
                               file_name=sensitivity_analysis_file_name)

        # Update sensitivity analysis section of settings object based on above selected choices
        settings.update(sensitivity_analysis_choices_inner_dict)

        # Execute simulation upon button press
        st.subheader("Run sensitivity analysis with choices selected above")
        # Execute simulation upon button press
        run_simulation_button_bool = st.button("Run simulation")
        if run_simulation_button_bool:
            # Run simulation
            with st.spinner(text="Running environmental and economic simulation. This may take ~60 seconds."):
                results = run_simulation()
                st.success("Simulation completed")
            show_simulation_results(results)
            download_zipped_figures(results)
