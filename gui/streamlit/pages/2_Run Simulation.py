import sys

from pathlib import Path

# Add root directory
root_path = str(Path(__file__).parent.parent.parent.parent)
sys.path.append(root_path)
# Note: Have all module imports after this

from config import settings

import streamlit as st
import pathlib
import os

from dynaconf import Dynaconf
from pathlib import Path
from run_LCA_example import run_LCA

# Ask user to upload toml file.
uploaded_file = st.file_uploader(label="Upload your user inputs file created in the 'Simulation Inputs' section",
                                 type="toml")

if uploaded_file is not None:  # Continue with script once a file has been uploaded

    run_simulation_button_bool = st.button("Run simulation with selected user input file")
    if run_simulation_button_bool:

        # Generate settings object to use for rest of simulation.
        def save_user_input_toml(uploaded_user_input_file):
            """
            Takes the user input data and writes it to a temporary file and creates a suitable path.
            Parameters
            ----------
            uploaded_user_input_file: UploadedFile
                User input .toml file uploaded by user.

            Returns
            -------

            """
            #
            data = uploaded_user_input_file.getvalue().decode('utf-8')
            parent_path = pathlib.Path(__file__).parent.resolve()
            save_path = os.path.join(parent_path, "user_inputs")
            complete_path = os.path.join(save_path, uploaded_file.name)

            with open(complete_path, "w") as destination_file:  # write data to user input file
                destination_file.write(data)

            return complete_path

        uploaded_user_inputs_path = save_user_input_toml(uploaded_file)
        # Get settings
        settings_updated = Dynaconf(
            settings_files=[  # Paths to toml files
                root_path + r"\configs\default_settings.toml",  # a file for default settings
                root_path + r"\configs\user_inputs_defaults.toml",  # default user inputs
                uploaded_user_inputs_path,  # user inputs (overwrites defaults)
                root_path + r"\configs\secrets.toml"  # a file for sensitive data (gitignored)
            ],
            environments=True,  # Enable layered environments
            merge_enabled=True  # Allows for default inputs to be overwritten
        )

        settings.update(settings_updated)  # update settings with file selected by user

        # Continue rest of script here

        with st.spinner(text="Running environmental and economic simulation. This may take ~60 seconds."):
            run_LCA()
        st.success("Simulation complete.")










        # Delete temporary user input file again
        os.remove(uploaded_user_inputs_path)
