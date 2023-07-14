import sys

from pathlib import Path


# Add root directory
root_path = str(Path(__file__).parent.parent.parent.parent)
sys.path.append(root_path)
# Note: Have all module imports after this

import toml

import streamlit as st

from human_id import generate_id

from config import settings
from functions.gui import display_correct_user_distribution_inputs
from functions.TEA import get_most_recent_available_CEPCI_year

# Background data
country_options = settings.general.countries
currency_options = settings.data.economic.currencies
feedstock_categories_options = settings.general.feedstock_categories
milling_screen_sizes_mm = settings.data.milling.screen_sizes
dryer_type_options = settings.streamlit.dryer_type_options
distribution_options = settings.background.distribution_options
economic_inputs_options = settings.streamlit.economic_inputs_options
numeric_inputs_options = settings.streamlit.numeric_inputs_options
pretreatment_options = settings.streamlit.pretreatment_options
carbon_capture_options = settings.streamlit.carbon_capture_options
CHP_options = settings.streamlit.CHP_options

# Start of streamlit app
st.title('Simulation Inputs')

# %% General simulation parameters
st.header("General simulation parameters")
MC_iterations = st.slider(label="Monte Carlo simulation iterations", min_value=100, max_value=10000, value=1000,
                          step=100)
country = st.selectbox(label="Country", options=country_options)

change_currency = st.checkbox(label="Select currency independently of country", value=False)

currency = None
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
particle_size_ar = st.number_input(label="Particle size [mm] (as received)", min_value=0.1, max_value=100.0, value=3.0,
                                   help="Please enter the feedstock's particle size in mm on an as received basis.")
milling_included = st.checkbox(label="Is feedstock milling included as a pretreatment step?", value=False)
milling_screen_size_mm = None
if milling_included:
    milling_screen_size_mm = st.selectbox(label="Milling screen size [mm]", options=milling_screen_sizes_mm,
                                          help="Screen sizes of 3.2, 4.76 and 6.5 mm result in approximate particle "
                                               "sizes of 16, 21, and 26 mm, respectively.")
    st.markdown("""---""")

st.subheader("Feedstock ultimate composition",
             help="Typical feedstock data may be obtained from the [Phyllis2 database](https://phyllis.nl).")
st.markdown("")
feedstock_C = st.number_input(label="Carbon content [%daf]", min_value=0.0, max_value=100.0)
feedstock_H = st.number_input(label="Hydrogen content [%daf]", min_value=0.0, max_value=100.0)
feedstock_N = st.number_input(label="Nitrogen content [%daf]", min_value=0.0, max_value=100.0)
feedstock_S = st.number_input(label="Sulphur content [%daf]", min_value=0.0, max_value=100.0)
feedstock_O_by_difference = 100 - feedstock_C - feedstock_H - feedstock_N - feedstock_S
feedstock_O = st.number_input(label="Oxygen content [%daf] (calculated by difference)", value=feedstock_O_by_difference,
                              min_value=0.0, max_value=100.0)
if feedstock_O < 0:
    st.error("Feedstock oxygen is below zero. Check imputed elemental composition.")
st.subheader("Feedstock proximate composition",
             help="Typical feedstock data may be obtained from the [Phyllis2 database](https://phyllis.nl).")
feedstock_moisture_ar = st.number_input(label="Feedstock moisture [%wb] (as received)", min_value=0.0, max_value=100.0)
drying_included = st.checkbox(label="Is feedstock drying included as a pretreatment step?", value=False)

# Set defaults
feedstock_moisture_post_drying = None
dryer_type = None
if drying_included:
    feedstock_moisture_post_drying = st.number_input(label="Desired feedstock moisture post drying [%wb]",
                                                     min_value=0.0, max_value=100.0)
    drying_additional_options = st.checkbox(label="Display additional drying options", value=False)
    if drying_additional_options:
        dryer_type = st.selectbox(label="Dryer type", options=dryer_type_options, index=0,
                                  help="Select which type of dryer is to be used.")
    st.markdown("""---""")
feedstock_ash = st.number_input(label="Ash content [%db]", min_value=0.0, max_value=100.0)

# %% Reactor information and processing conditions
st.header("Reactor information and processing conditions")

temperature = st.number_input(label="Gasification temperature [°C]", min_value=0.0, max_value=1500.0, value=750.0)
ER = st.number_input(label="Equivalence Ratio (ER)", min_value=0.0, max_value=1.0, value=0.3,
                     help="The equivalence ratio (ER) is the ratio between the oxygen content in the oxidant supply "
                          "and that required for complete stoichiometric combustion.")

operation_mode = st.radio(label="Operation mode", options=["Continuous", "Batch"])
operation_scale = st.radio(label="Operation scale", options=["Lab", "Pilot"])
catalyst = st.radio(label="Catalyst use", options=("No", "Yes"),
                    help="Please select whether a catalyst of any form is used.")

gasifying_agent = st.selectbox(label="Gasifying agent", options=["Air", "Oxygen", "Steam", "Other"])
# currently "Air + Steam not supported

reactor_type = st.selectbox(label="Reactor type", options=["Fixed bed", "Fluidised bed", "Other"])

bed_material = "N/A"
if reactor_type != "Fixed bed":
    bed_material = st.selectbox(label="Reactor bed material", options=["Silica", "Alumina", "Olivine", "Other"])
    st.markdown("""---""")

# %% Techno-economic analysis inputs
st.header("Techno-economic analysis choices")

CEPCI_year = st.number_input("Select the year to which prices should be updated to",
                             value=get_most_recent_available_CEPCI_year(),
                             step=1,
                             min=2001,
                             max=get_most_recent_available_CEPCI_year(),
                             help="Generally the default year is the most recent CEPCI value."
                             )
st.markdown("""---""")

electricity_price = st.selectbox(label="Select the electricity wholesale price [" + currency + "/kWh]",
                                 options=economic_inputs_options)
electricity_price_parameters = {}
if electricity_price == "user selected":
    electricity_price_user_selected = st.radio(label="Distribution type", options=distribution_options, index=0,
                                               key="electricity price distribution type")
    electricity_price_parameters = display_correct_user_distribution_inputs(choice=electricity_price_user_selected,
                                                                            key="electricity price distribution " +
                                                                                electricity_price_user_selected)
    st.markdown("""---""")

heat_price = st.selectbox(label="Select the heat/thermal energy wholesale price [" + currency + "/kWh]",
                          options=economic_inputs_options)
heat_price_parameters = {}
if heat_price == "user selected":
    heat_price_user_selected = st.radio(label="Distribution type", options=distribution_options, index=0,
                                        key="heat price distribution type")
    heat_price_parameters = display_correct_user_distribution_inputs(choice=heat_price_user_selected,
                                                                     key="heat price distribution " +
                                                                         heat_price_user_selected)
    st.markdown("""---""")


# TODO: Add other user inputs required for economic analysis


# %% Process selection and process choices.
st.header("Process selector")
st.write("Select which processes are to be considered in your gasification model.")
st.write("Additional inputs can be given for some processes. These make the analysis more case specific, but the "
         "required data may be difficult to obtain. If data is unavailable it is recommended to select the default "
         "option.")

# %% Pretreatment:
st.subheader("Pretreatment options")
# Get default options for pretreatment based on earlier selections
pretreatment_default_options_displayed = []
if drying_included:
    pretreatment_default_options_displayed.append("Drying")
if milling_included:
    pretreatment_default_options_displayed.append("Milling")

pretreatment_choices = st.multiselect(label="Select the considered pretreatment processes", options=pretreatment_options,
                                      default=pretreatment_default_options_displayed,
                                      help="Please define which pretreatment options are to be used before the "
                                           "feedstock is used for gasification.")

# Check that earlier selections regarding pretreatment match with selection now.
if "Drying" in pretreatment_choices and not drying_included:
    st.error("Feedstock drying previously omitted.")
if "Milling" in pretreatment_choices and not milling_included:
    st.error("Feedstock milling previously omitted.")
if "Drying" not in pretreatment_choices and drying_included:
    st.error("Feedstock drying previously included.")
if "Milling" not in pretreatment_choices and milling_included:
    st.error("Feedstock milling previously included.")

# Add variables for included processes
if "Drying" in pretreatment_choices:
    drying_included = True
else:
    drying_included = False
if "Milling" in pretreatment_choices:
    milling_included = True
else:
    milling_included = False
if "Pelleting" in pretreatment_choices:
    pelleting_included = True
else:
    pelleting_included = False
if "Bale shredding" in pretreatment_choices:
    bale_shredding_included = True
else:
    bale_shredding_included = False

# %% Biochar application
st.subheader("Biochar application to soil")
biochar_included = st.checkbox(label="Select to include biochar for soil application", value=True)

# Set defaults
biochar_yield = None
biochar_carbon_fraction = None
biochar_stability = None

if biochar_included:
    biochar_yield_option = st.radio(label="Biochar yield", options=numeric_inputs_options)
    if biochar_yield_option == "default":
        biochar_yield = None
    else:
        biochar_yield = st.number_input(label="Biochar yield [g/kg wb]")

    biochar_carbon_fraction_option = st.radio(label="Biochar carbon fraction", options=numeric_inputs_options)
    if biochar_carbon_fraction_option == "default":
        biochar_carbon_fraction = None
    else:
        biochar_carbon_fraction = st.number_input(label="Biochar carbon fraction as a decimal")

    biochar_stability_option = st.radio(label="Recalcitrant fraction of carbon in biochar",
                                        options=numeric_inputs_options)
    if biochar_stability_option == "default":
        biochar_stability = None
    else:
        biochar_stability = st.number_input(label="Recalcitrant fraction of carbon in biochar as a decimal")
    st.markdown("""---""")

# %% Carbon capture
st.subheader("Carbon capture and storage (CCS)")
carbon_capture_included = st.checkbox(label="Select to include CCS", value=False)
carbon_capture_method = None  # set default

if carbon_capture_included:
    carbon_capture_method = st.radio(label="Display additional inputs", options=carbon_capture_options)
    if carbon_capture_method == "Vacuum pressure swing adsorption (VPSA) post combustion capture (default)":
        carbon_capture_method = "VPSA post combustion"
    elif carbon_capture_method == "Amine-based post combustion capture":
        carbon_capture_method = "Amine post comb"

# %% Combined heat and power (CHP) plant
st.subheader("Optional user inputs")
CHP_display_additional_inputs = st.checkbox(label="Display additional combined heat and power (CHP) inputs",
                                            value=False, key="CHP")
CHP_dict = {}
if CHP_display_additional_inputs:
    CHP_unit = st.radio(label="Display additional inputs", options=CHP_options)
    # Set defaults
    CHP_electrical_efficiency = None
    CHP_thermal_efficiency = None
    CHP_parasitic_energy_demand = None
    CHP_size_kW = None
    if CHP_unit == "User defined":
        CHP_electrical_efficiency = st.number_input(label="Electrical efficiency as a decimal",
                                                    min_value=0, max_value=1)
        CHP_thermal_efficiency = st.number_input(label="Thermal efficiency as a decimal", min_value=0, max_value=1)
        CHP_parasitic_energy_demand = st.number_input(label="Parasitic energy demand as a decimal",
                                                      min_value=0, max_value=1)
        CHP_size_kW = st.number_input(label="CHP plant size [kW]")

    CHP_dict = {"type": CHP_unit,
                "electrical_efficiency": CHP_electrical_efficiency,
                "thermal_efficiency": CHP_thermal_efficiency,
                "parasitic_demand": CHP_parasitic_energy_demand,
                "size_kW": CHP_size_kW
                }

# %% Closing section - compile results and download
st.header("Compile user inputs and download")


def user_data_to_toml():

    # Generate file name
    ID = generate_id()
    user_inputs_file_name = "user_inputs_" + ID + ".toml"

    # Store data
    user_inputs_dict = {
        "default": {
            "user_inputs": {
                "general": {"MC_iterations": MC_iterations,
                            "country": country,
                            "currency": currency
                            },

                "feedstock": {"category": feedstock_category,  # general
                              "name": feedstock_name,
                              "particle_size_ar": particle_size_ar,
                              "carbon": feedstock_C,  # ultimate composition
                              "hydrogen": feedstock_H,
                              "nitrogen": feedstock_N,
                              "sulphur": feedstock_S,
                              "oxygen": feedstock_O,
                              "moisture_ar": feedstock_moisture_ar,  # proximate
                              "moisture_post_drying": feedstock_moisture_post_drying,
                              "ash": feedstock_ash,
                              },

                "process_conditions": {"gasification_temperature": temperature,
                                       "ER": ER,
                                       "operation_mode": operation_mode,
                                       "operation_scale": operation_scale,
                                       "catalyst": catalyst,
                                       "gasifying_agent": gasifying_agent,
                                       "reactor_type": reactor_type,
                                       "bed_material": bed_material
                                       },

                "economic": {"CEPCI_year": CEPCI_year,
                             "electricity_price_choice": electricity_price,
                             "electricity_price_parameters": electricity_price_parameters,
                             "heat_price_choice": heat_price,
                             "heat_price_parameters": heat_price_parameters
                             },

                "processes": {
                    # Pretreatment
                    "milling": {"included": milling_included,
                                "screen_size_mm": milling_screen_size_mm
                                },
                    "drying": {"included": drying_included,
                               "moisture_post_drying": feedstock_moisture_post_drying,
                               "dryer_type": dryer_type
                               },
                    "pelleting": {"included": pelleting_included},
                    "bale_shredding": {"included": bale_shredding_included},

                    # Biochar use
                    "biochar": {"included": biochar_included,
                                "biochar_yield": biochar_yield,
                                "biochar_carbon_fraction": biochar_carbon_fraction,
                                "biochar_stability": biochar_stability
                                },
                    "carbon_capture": {"included": carbon_capture_included,
                                       "method": carbon_capture_method
                                       },
                    "CHP": CHP_dict
                }
            }
        }
    }
    return user_inputs_dict, user_inputs_file_name


if st.button(label='Compile Data'):
    st.success("Data successfully compiled. Download below.")
    # Create the dictionary
    data, file_name = user_data_to_toml()
    # Serialize the dictionary to a string using TOML
    toml_data = toml.dumps(data).encode('utf-8')
    # Create a download button that allows the user to download the TOML file
    st.download_button(label='Download Data', data=toml_data, file_name=file_name)
