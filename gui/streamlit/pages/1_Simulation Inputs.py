import toml

import streamlit as st

from human_id import generate_id

# from config import settings
# TODO: Integrate with dynaconf and my other personal libraries of the project. Think I would have to turn my own work
#  into a package first.
# country_options = settings.general.countries
# currency_options = settings.data.economic.currencies

# Data
country_options = ["UK", "USA", "Germany"]
currency_options = ["GBP", "USD", "EUR"]
feedstock_categories_options = ["plastics", "municipal solid waste", "herbaceous biomass", "woody biomass",
                                "sewage sludge", "other"]
milling_screen_sizes_mm = [3.20, 4.76, 6.50]
distribution_options = ["fixed", "range", "triangular", "gaussian"]
economic_inputs_options = ["default", "user selected", "predefined scenario"]

# Start of streamlit app
st.title('Simulation Inputs')

# %% General simulation parameters
st.header("General simulation parameters")
MC_iterations = st.slider(label="Monte Carlo simulation iterations", min_value=100, max_value=10000, value=1000,
                          step=100)

country = st.selectbox(label="Country", options=country_options)

change_currency = st.checkbox(label="Select currency independently of country", value=False)

if change_currency:
    currency = st.selectbox(label="Currency", options=currency_options)
else:  # set currency based on country selection
    if country == "UK":
        currency = "GBP"
    elif country == "USA":
        currency = "USD"
    elif country == "Germany":
        currency = "EUR"

# %% Feedstock information
st.header("Feedstock information")
st.subheader("General feedstock information")
feedstock_category = st.selectbox(label="Feedstock category", options=feedstock_categories_options, index=2)
feedstock_name = st.text_input(label="Feedstock name", placeholder="Please enter the name of your feedstock")
particle_size_ar = st.number_input(label="Particle size [mm] (as received)", min_value=0.1, max_value=100.0,
                                   help="Please enter the feedstock's particle size in mm on an as received basis.")
milling_included = st.checkbox(label="Is feedstock milling included as a pretreatment step?", value=False)
if milling_included:
    milling_screen_sizes_mm = st.selectbox(label="Milling screen size [mm]", options=milling_screen_sizes_mm,
                                           help="Screen sizes of 3.2, 4.76 and 6.5 mm result in approximate particle "
                                                "sizes of 16, 21, and 26 mm, respectively. ")

st.subheader("Feedstock ultimate composition")
feedstock_C = st.number_input(label="Carbon content [%daf]", min_value=0.0, max_value=100.0)
feedstock_H = st.number_input(label="Hydrogen content [%daf]", min_value=0.0, max_value=100.0)
feedstock_N = st.number_input(label="Nitrogen content [%daf]", min_value=0.0, max_value=100.0)
feedstock_S = st.number_input(label="Sulphur content [%daf]", min_value=0.0, max_value=100.0)
feedstock_O = 100 - feedstock_C - feedstock_H - feedstock_N - feedstock_S
st.markdown(("The feedstock's oxygen content has been calculated by difference as: " + str(feedstock_O) + " %daf"))
if feedstock_O < 0:
    st.error("Feedstock oxygen is below zero. Check imputed elemental composition.")
st.subheader("Feedstock proximate composition")
feedstock_moisture_ar = st.number_input(label="Feedstock moisture [%wb] (as received)", min_value=0.0, max_value=100.0)
drying_included = st.checkbox(label="Is feedstock drying included as a pretreatment step?", value=False)
if drying_included:
    feedstock_moisture_post_drying = st.number_input(label="Desired feedstock moisture post drying [%wb]",
                                                     min_value=0.0, max_value=100.0)

feedstock_ash = st.number_input(label="Ash content [%db]", min_value=0.0, max_value=100.0)

# %% Reactor information and processing conditions
st.header("Reactor information and processing conditions")

temperature = st.number_input(label="Gasification temperature [°C]", min_value=0.0, max_value=1500.0, value=750.0)
ER = st.number_input(label="Equivalence Ratio (ER)", min_value=0.0, max_value=1.0, value=0.3,
                     help="The equivalence ratio (ER) is the ratio between the oxygen content in the oxidant supply "
                          "and that required for complete stoichiometric combustion.")

operation_mode = st.radio(label="Operation mode", options=["Continuous", "Batch"])
operation_scale = st.radio(label="Operation mode", options=["Lab", "Pilot"])
catalyst = st.radio(label="Catalyst use", options=("No", "Yes"),
                    help="Please select whether a catalyst of any form is used.")

gasifying_agent = st.selectbox(label="Gasifying agent", options=["Air", "Oxygen", "Steam", "Other"])
# currently "Air + Steam not supported

reactor_type = st.selectbox(label="Reactor type", options=["Fixed bed", "Fluidised bed", "Other"])

bed_material = None
if reactor_type != "Fixed bed":
    bed_material = st.selectbox(label="Reactor bed material", options=["Silica", "Alumina", "Olivine", "Other"])

# %% Techno-economic analysis inputs
st.header("Techno-economic analysis choices")


def display_correct_user_distribution_inputs(choice):
    """
    Displays the correct input fields based on the user's selected distribution type.
    Parameters
    ----------
    choice

    Returns
    -------
        Given user inputs.
    """
    dist_values = None
    if choice == "fixed":
        value = st.number_input(label="Constant value")
        dist_values = (value,)
    elif choice == "range":
        low = st.number_input(label="Distribution lower bound")
        high = st.number_input(label="Distribution upper bound")
        dist_values = (low, high)
    elif choice == "triangular":
        lower = st.number_input(label=" Distribution lower bound")
        mode = st.number_input(label="Distribution mode")
        upper = st.number_input(label="Distribution upper bound")
        dist_values = (lower, mode, upper)

    elif choice == "gaussian":
        mean = st.number_input(label="Distribution mean")
        std = st.number_input(label="Distribution standard deviation (σ)")
        dist_values = (mean, std)


        # TODO: Turn output into dictionary of this type - i.e. key value pairs with parameters (e.g. lower, upper) and
        #  distribution_type parameter - add units at later point outside the function.
                        # lower = 0.100
                        # mode = 0.16127  # as of 23rd of January 2023 https://www.ofgem.gov.uk/cy/energy-data-and-research/data-portal/wholesale-market-indicators
                        # upper = 0.200
                        # units = "GBP/kWh"
                        # distribution_type = "triangular"

    return dist_values


electricity_price = st.radio(label="Select the electricity wholesale price [" + currency + "/kWh]",
                             options=economic_inputs_options)
if electricity_price == "user selected":
    electricity_price_user_selected = st.radio(label="Distribution type", options=distribution_options, index=0)
    electricity_price_user_selected_choices = display_correct_user_distribution_inputs(electricity_price_user_selected)
elif electricity_price == "predefined scenario":
    # TODO: Add predefined scenarios
    pass

# TODO: Add other user inputs required for economic analysis


# %% Process selection and process choices.
st.header("Processes considered in gasification scheme")

# TODO: Implement way to make choices about process parameters and link to model (see comment below)
# """
# i.e. pretreatment, carbon capture, CHP unit options - save all these in intelligent format
# e.g. [default.user_inputs.process_XYZ.CHP_unit_choice]
# think about whether this should be dynaconf format - would need to then change settings path to the newly created
#  file when running
# could have something like this as order - default_settings (first looked at), overwritten by (default_user_inputs),
# overwritten by (user_added_user_inputs) - in theory I should be able to leave things blank in 3rd file and it would
# default to parameters from 2nd or even 1st file
# """















# %% Closing section
st.header("Compile user inputs and download")


# # # # # # # # # # # DIRECT ATTTEMPT  # # # # # # # # # # # #

import toml

def get_data_to_toml():

    # Generate file name
    ID = generate_id()
    file_name = "user_inputs_" + ID + ".toml"
    # TODO: Add all data to file

    # EXAMPLE
    data = {
        "default": {
            "general": {"MC_iterations": MC_iterations,
                        "country": country},
            "feedstock": {"category": feedstock_category}
        }
    }

    return data, file_name


    # Create new toml file and generate ID for it




if st.button('Compile Data'):
    # Create the dictionary
    data, file_name = get_data_to_toml()
    # Serialize the dictionary to a string using TOML
    toml_data = toml.dumps(data).encode('utf-8')
    # Create a download button that allows the user to download the TOML file
    st.download_button(label='Download Data', data=toml_data, file_name=file_name)












# # # # # # # # # # # TOMLKIT ATTTEMPT  # # # # # # # # # # # #


from tomlkit import document, comment

# def compile_user_inputs():
#
#     toml = document()
#

#     ID = generate_id()
#     file_name = "user_inputs_" + ID + ".toml"
#
#     toml.add("electricity price", 123)
#
#     return file_name





# # # # # # # # # # # TEMPFILE ATTTEMPT  # # # # # # # # # # # #
# import tempfile
#
# def create_new_toml():
#
#     # Create new toml file and generate ID for it
#     ID = generate_id()
#     file_name = "user_inputs_" + ID + ".toml"
#     temp_file = tempfile.TemporaryFile(mode="r")
#
#     # TODO: FIX THIS currently some issues with with file_path - creates new file when calling just file_name with open
#     #  and return that - maybe that would work too where file is create in cache and never saved locally
#
#     # TODO: NOTE - the function works when isolated and actually creates the empty file - but when called in streamlit it causes problems and the file does not seem to get generated
#     return temp_file, file_name
#
#
# def fill_new_toml(temp_file):
#
#     # TODO: Add all data to file
#
#     # EXAMPLE
#     data = {
#         "default": {
#             "general": {"MC_iterations": MC_iterations,
#                         "country": country},
#             "feedstock": {"category": feedstock_category}
#         }
#
#     }
#     return temp_file
#
#     # temp_file.write("sfsfasfr")
#
#     # # Turn data into correct format for storage
#     #
#     # # Convert reactor type before storing in toml
#     # if reactor_type == 'Fixed bed':
#     #     reactor_type_value_to_toml = 'Fixed'
#     # elif reactor_type == 'Fluidised bed':
#     #     reactor_type_value_to_toml = 'Fluidised'
#     # else:
#     #     reactor_type_value_to_toml = 'Other'
#     #
#     # # Fix bed material values for fixed bed_reactor
#     # if reactor_type == "Fixed bed":
#     #     bed_material_to_toml = 'N/A'
#     # else:
#     #     bed_material_to_toml = bed_material
#     #
#     # # Cases where these are not selected
#     # if not change_currency:
#     #     pass
#     # if not milling_included:
#     #     pass
#     # if not drying_included:
#     #     pass
#
#
#
#
# user_inputs_compiled = st.button(label="Compile user inputs now")
# if user_inputs_compiled:
#     user_inputs_file_path, user_inputs_file_name = create_new_toml()
#     file = fill_new_toml(user_inputs_file_path)
#     st.write("User inputs have been compiled and saved to the following file:", user_inputs_file_name)
#     st.download_button("Download settings file containing user inputs", data=file,
#                        file_name=user_inputs_file_name)





# # # # # # # # # # # create file, then write to it attempt  # # # # # # # # # # # #


# # Create new toml file and generate ID for it
# ID = generate_id()
# file_name = "user_inputs_" + ID + ".toml"
# file_path = "user_inputs\\" + file_name
#
# with open(file_path, "w"):
#     pass
#
# # TODO: FIX THIS currently some issues with with file_path - creates new file when calling just file_name with open
# #  and return that - maybe that woudl work too where file is create in cache and never saved locally
#
# # TODO: NOTE - the function works when isolated and actually creates the empty file - but when called in streamlit it causes problems and the file does not seem to get generated
#
# return file_path, file_name
#
# def fill_new_toml(file_path):
#
#     # TODO: Add all data to file
#
#     # EXAMPLE
#     data = {
#         "default": {
#             "general": {"MC_iterations": MC_iterations,
#                         "country": country},
#             "feedstock": {"category": feedstock_category}
#         }
#
#     }
#
#     # Update toml
#     with open(file_path, 'w') as f:
#         toml.dump(data, f)
#
#
#     # Turn data into correct format for storage
#
#     # Convert reactor type before storing in toml
#     if reactor_type == 'Fixed bed':
#         reactor_type_value_to_toml = 'Fixed'
#     elif reactor_type == 'Fluidised bed':
#         reactor_type_value_to_toml = 'Fluidised'
#     else:
#         reactor_type_value_to_toml = 'Other'
#
#     # Fix bed material values for fixed bed_reactor
#     if reactor_type == "Fixed bed":
#         bed_material_to_toml = 'N/A'
#     else:
#         bed_material_to_toml = bed_material
#
#     # Cases where these are not selected
#     if not change_currency:
#         pass
#     if not milling_included:
#         pass
#     if not drying_included:
#         pass
#
#
#
#
# user_inputs_compiled = st.button(label="Compile user inputs now")
# if user_inputs_compiled:
#     user_inputs_file_path, user_inputs_file_name = create_new_toml()
#     fill_new_toml(user_inputs_file_path)
#     st.write("User inputs have been compiled and saved to the following file:", user_inputs_file_name)
#     st.download_button("Download settings file containing user inputs", data=user_inputs_file_path,
#                        file_name=user_inputs_file_name)


























# # %% Closing section
# st.header("Compile user inputs and download")
#
# from tomlkit import document, comment
#
# # def compile_user_inputs():
# #
# #     toml = document()
# #
#
# #     ID = generate_id()
# #     file_name = "user_inputs_" + ID + ".toml"
# #
# #     toml.add("electricity price", 123)
# #
# #     return file_name
#
#
#
#
#
#
#
#
# #
# # with open("new_toml.toml", "w") as new_file:
# #     pass
#
#
# def compile_user_inputs():
#
#     # Create new toml file and generate ID for it
#     ID = generate_id()
#     file_name = "user_inputs_" + ID + ".toml"
#     file_path = "user_inputs\\" + file_name
#     new_file = open(file_name, "w")
#     new_file.close()
#     # TODO: Add all data to file
#
#     # # EXAMPLE
#     # data = {
#     #     "default": {
#     #         "general": {"MC_iterations": MC_iterations,
#     #                     "country": country},
#     #         "feedstock": {"category": feedstock_category}
#     #     }
#     #
#     # }
#     #
#     # data
#     #
#     # # Update toml
#     # with open(file_path, 'w') as f:
#     #     toml.dump(data, f)
#
#
#     # Turn data into correct format for storage
#
#     # Convert reactor type before storing in toml
#     if reactor_type == 'Fixed bed':
#         reactor_type_value_to_toml = 'Fixed'
#     elif reactor_type == 'Fluidised bed':
#         reactor_type_value_to_toml = 'Fluidised'
#     else:
#         reactor_type_value_to_toml = 'Other'
#
#     # Fix bed material values for fixed bed_reactor
#     if reactor_type == "Fixed bed":
#         bed_material_to_toml = 'N/A'
#     else:
#         bed_material_to_toml = bed_material
#
#     # Cases where these are not selected
#     if not change_currency:
#         pass
#     if not milling_included:
#         pass
#     if not drying_included:
#         pass
#
#
#     return file_path, file_name
#
#
# user_inputs_compiled = st.button(label="Compile user inputs now")
# if user_inputs_compiled:
#     user_inputs_file_path, user_inputs_file_name = compile_user_inputs()
#     st.write("User inputs have been compiled and saved to the following file:", user_inputs_file_name)
#     st.download_button("Download settings file containing user inputs", data=user_inputs_file_path,
#                        file_name=user_inputs_file_name)
