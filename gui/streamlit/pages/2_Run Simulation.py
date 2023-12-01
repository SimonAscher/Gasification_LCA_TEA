import sys

from pathlib import Path


# Add root directory
root_path = str(Path(__file__).parent.parent.parent.parent)
sys.path.append(root_path)
# Note: Have all module imports after this

import streamlit as st

from functions.MonteCarloSimulation import run_simulation
from functions.gui.streamlit_helpers import update_settings_with_user_inputs, show_simulation_results, \
    download_zipped_figures

# Ask user to upload toml file.
uploaded_file = st.file_uploader(label="Upload your user inputs file created in the 'Simulation Inputs' section",
                                 type="toml")

if uploaded_file is not None:  # Continue with script once a file has been uploaded
    # Update settings with uploaded user inputs. This also resets sensitivity analysis values if previously selected.
    update_settings_with_user_inputs(uploaded_file)

    # Execute simulation upon button press
    run_simulation_button_bool = st.button("Run simulation")
    if run_simulation_button_bool:
        # Run simulation
        with st.spinner(text="Running environmental and economic simulation. This may take ~60 seconds."):
            results = run_simulation()
            st.success("Simulation completed")
        show_simulation_results(results)
        download_zipped_figures(results)
