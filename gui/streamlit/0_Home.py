# %% Imports and fix root directory

import sys

import streamlit as st

from pathlib import Path

# Add root directory
root_path = str(Path(__file__).parent.parent.parent)
sys.path.append(root_path)
# Note: Have all module imports after this

#%% Main Program - TESTS

st.title('General Biomass and Waste Gasification LCA and TEA')

st.write("TODO: ADD INTRODUCTION HERE - This is a model for - the model is strutured as such - the gui is structured in this way - etc.")
