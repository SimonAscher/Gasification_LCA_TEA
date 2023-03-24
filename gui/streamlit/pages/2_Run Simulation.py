import streamlit as st

# Start of streamlit app
st.title('Run simulation')

user_inputs_file = st.file_uploader(label="Upload your user inputs file created in the 'Simulation Inputs' section",
                                    type="toml")

# get process inputs here


pretreatment_options = ["Drying", "Milling", "Pelleting", "Bale shredding"]

pretreatment_options = st.multiselect(label="Pretreatment options", options=pretreatment_options,
                                      help="Please define which pretreatment options are to be used before the "
                                           "feedstock is used for gasification.")



