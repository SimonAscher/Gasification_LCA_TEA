import streamlit as st

st.title('General Biomass and Waste Gasification LCA and TEA')


# Add root directory
import sys
sys.path.append('/')

# dynaconf tests
# from dynaconf import Dynaconf
# settings = Dynaconf(settings_files=['configs/default_settings.toml'])

from config import settings

# from dynaconf import LazySettings
#
# settings_module = ".config"  # Replace with the correct module name
#
# settings_files = ["configs/default_settings.toml"]  # Replace with the correct settings files
# settings = LazySettings(settings_module, settings_files=settings_files)
# print(settings_files)
# print(settings)


from dynaconf import LazySettings



# st.write(f"Type of settings: {type(settings)}")
# st.write(f"Contents of settings: {settings.keys()}")
# st.write(f"Contents of settings: {settings.as_dict()}")  # shows empty
# st.write(settings)
# st.write(f"Contents of settings: {settings.default.background.iteration_MC}")
# st.write(f"Contents of settings: {settings.user_inputs.general.MC_iterations}")



# this fixed path and functions now work (if simple function defined in function folder and e.g. called my_functions.py
# with function my_func() - but dynaconf still does not

# st.write(settings.get("background"))
#
# from functions.TEA.scaling import power_scale
# b = power_scale(1000,100,80)
# st.write(b)


st.write(sys.path)
st.write("hello world")

# TODO: Finish trouble shooting why dynaconf does not load properly...