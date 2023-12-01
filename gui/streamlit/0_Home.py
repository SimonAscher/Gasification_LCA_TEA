# %% Imports and fix root directory

import sys
import os

import streamlit as st

from pathlib import Path

# Add root directory
root_path = str(Path(__file__).parent.parent.parent)
sys.path.append(root_path)
# Note: Have all module imports after this

#%% Main Content

st.title("A Model for the Rapid Assessment of the Environmental and Economic Impacts of Biomass and Waste "
         "Gasification Schemes")

st.header("Summary")
st.markdown("""
This work presents a framework to conduct **life cycle assessment (LCA)** and **techno-economic analysis (TEA)** of 
biomass and waste gasification schemes. Machine learning (ML), in the form of a **gradient boosting** model, is utilised
to predict the composition and yields of gasification products. Uncertainties resulting from the machine learning model 
and other uncertainties throughout the model framework are accounted for through **Monte Carlo simulation** methodology.
""")

st.header("How to use the model")
st.markdown("""
The side bar on the left-hand side lets you navigate through the program.
- You will need to define the inputs to your simulation in **Section 1 - Simulation Inputs**. Here you will define 
information which will be used in the simulation (e.g. the feedstock used, the gasification operating conditions, and 
how much the generated energy can be sold for. Finally you can download a `.toml` file which can be used to run your 
the model in **Section 2 - Run Simulation**.
- **Section 2 - Run Simulation** lets you upload the `.toml` user input file generated in the previous section, which 
will then be used to run the simulation. 
""")

st.header("Video example")
st.video(os.path.join(root_path, r"gui\streamlit\pages\data\streamlit_example.mp4"))
