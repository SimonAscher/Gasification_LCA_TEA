# %% Imports and fix root directory

import sys

import streamlit as st

from pathlib import Path

# Add root directory
root_path = str(Path(__file__).parent.parent.parent)
sys.path.append(root_path)
# Note: Have all module imports after this

#%% Main Program - TESTS
from processes.syngas_combustion import SyngasCombustion

st.title('General Biomass and Waste Gasification LCA and TEA')

# Test streamlit
a = SyngasCombustion()
st.write(a.GWP_mean)
