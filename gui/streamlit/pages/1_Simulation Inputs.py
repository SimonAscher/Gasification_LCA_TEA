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
from functions.general import (convert_system_size, calculate_LHV_HHV_feedstock_from_direct_inputs,
                               calculate_LHV_from_HHV)

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

system_life_span = int(st.number_input("The system's life span [years]", min_value=10, max_value=30, value=20, step=1,
                                       help="This typically ranges between 15 and 30 years."))

annual_operating_hours_check = st.checkbox("Are the annual operating hours known?",
                                           help="If this is not known an estimate based on empirical data will be "
                                                "made.")
annual_operating_hours_value = None
if annual_operating_hours_check:
    annual_operating_hours_value = int(st.number_input("The system's annual operating hours [hours/year]",
                                                       min_value=5000, max_value=8760, value=8000, step=1,
                                                       help="This typically ranges between 6000 and 8500 hours/year."))
    st.divider()

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
    elif country == "Germany" or country == "EU":
        currency = "EUR"

# %% Feedstock information
st.header("Feedstock information")
st.subheader("General feedstock information")
feedstock_name = st.text_input(label="Feedstock name", placeholder="Please enter the name of your feedstock")
feedstock_category = st.selectbox(label="Feedstock category", options=feedstock_categories_options, index=2)

# Allow user to enter biogenic carbon fraction for certain waste types
biogenic_carbon_fraction = None
if feedstock_category in ["municipal solid waste", "sewage sludge", "other"]:
    custom_biogenic_fraction_included = st.checkbox(label="Would you like to select a custom biogenic to fossil "
                                                          "fraction of your feedstock?", value=False)
    if custom_biogenic_fraction_included:
        biogenic_carbon_fraction = st.slider(label="Biogenic fraction of the feedstock [%]",
                                             min_value=0,
                                             max_value=100,
                                             value=50,
                                             step=1,
                                             help="A value of 0% would represent a fossil feedstock, whereas a value of"
                                                  " 100% would represent a completely biogenic feedstock.")
        biogenic_carbon_fraction /= 100  # turn into a decimal
        st.markdown("""---""")


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
             help="Typical feedstock data may be obtained from the [Phyllis2](https://phyllis.nl) database.")
st.markdown("")
feedstock_C = st.number_input(label="Carbon content [%daf]", min_value=0.0, max_value=100.0)
feedstock_H = st.number_input(label="Hydrogen content [%daf]", min_value=0.0, max_value=100.0)
feedstock_N = st.number_input(label="Nitrogen content [%daf]", min_value=0.0, max_value=100.0)
feedstock_S = st.number_input(label="Sulphur content [%daf]", min_value=0.0, max_value=100.0)
feedstock_O_by_difference = 100 - feedstock_C - feedstock_H - feedstock_N - feedstock_S
feedstock_O = st.number_input(label="Oxygen content [%daf] (calculated by difference)", value=feedstock_O_by_difference,
                              min_value=0.0, max_value=100.0)
if feedstock_O < 0:
    st.error("Feedstock oxygen is below 0 %. Check imputed elemental composition.")
st.subheader("Feedstock proximate composition",
             help="Typical feedstock data may be obtained from the [Phyllis2 database](https://phyllis.nl).")
feedstock_moisture_ar = st.number_input(label="Feedstock moisture [%wb] (as received)", min_value=0.0, max_value=100.0)
drying_included = st.checkbox(label="Is feedstock drying included as a pretreatment step?", value=False)

# Set defaults
feedstock_moisture_post_drying = None
dryer_type = None
if drying_included:
    feedstock_moisture_post_drying = st.number_input(label="Desired feedstock moisture post drying [%wb]",
                                                     value=feedstock_moisture_ar,
                                                     min_value=0.0,
                                                     max_value=feedstock_moisture_ar)
    drying_additional_options = st.checkbox(label="Display additional drying options", value=False)
    if drying_additional_options:
        dryer_type = st.selectbox(label="Dryer type", options=dryer_type_options, index=0,
                                  help="Select which type of dryer is to be used.")
    st.markdown("""---""")
feedstock_ash = st.number_input(label="Ash content [%db]", min_value=0.0, max_value=100.0)

st.subheader("Feedstock energy")
feedstock_LHV_given_by_user = st.checkbox("Is the feedstock's lower heating value (LHV) or higher heating value (HHV) "
                                          "(also known as net calorific value or gross calorific value, respectively) "
                                          "known? If not it will be estimated based on the feedstock's ultimate "
                                          "and proximate composition.")
if feedstock_LHV_given_by_user:
    LHV_HHV_switch = st.selectbox(label="Decide whether you would like to enter the value as a LHV or HHV",
                                  options=["LHV", "HHV"])
    if LHV_HHV_switch == "LHV":
        feedstock_LHV = st.number_input(label="Feedstock LHV [MJ/kg wb]", min_value=0.0, max_value=50.0)
    else:
        feedstock_HHV = st.number_input(label="Feedstock HHV [MJ/kg wb]", min_value=0.0, max_value=50.0)
        if drying_included:
            feedstock_LHV = calculate_LHV_from_HHV(HHV=feedstock_HHV, H=feedstock_H,
                                                   moisture=feedstock_moisture_post_drying)
        else:
            feedstock_LHV = calculate_LHV_from_HHV(HHV=feedstock_HHV, H=feedstock_H,
                                                   moisture=feedstock_moisture_ar)
        if feedstock_HHV != 0:
            if feedstock_C != 0 or feedstock_H != 0 or feedstock_N != 0 or feedstock_S != 0:
                st.write(f"Estimated feedstock LHV is {feedstock_LHV:.2f} MJ/kg wb.")

else:
    if drying_included:
        feedstock_LHV = calculate_LHV_HHV_feedstock_from_direct_inputs(C=feedstock_C, H=feedstock_H, O=feedstock_O,
                                                                       moisture=feedstock_moisture_post_drying)
    else:
        feedstock_LHV = calculate_LHV_HHV_feedstock_from_direct_inputs(C=feedstock_C, H=feedstock_H, O=feedstock_O,
                                                                       moisture=feedstock_moisture_ar)
    if feedstock_C != 0 or feedstock_H != 0 or feedstock_N != 0 or feedstock_S != 0:  # only display after user inputs
        st.write(f"Estimated feedstock LHV is {feedstock_LHV:.2f} MJ/kg wb.")

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

if reactor_type == "Fluidised bed":
    bed_material = st.selectbox(label="Reactor bed material", options=["Silica", "Alumina", "Olivine", "Other"])
    st.markdown("""---""")
elif reactor_type == "Other":
    bed_material = st.selectbox(label="Reactor bed material", options=["Silica", "Alumina", "Olivine", "Other", "N/A"])
    st.markdown("""---""")
else:
    bed_material = "N/A"

# %% System size
st.header("System size information")

st.write("Please define the system size based on at least one of the three metrics. More than one metric can be "
         "defined. If not all size metrics are defined, the others will be estimated.")
system_size_mass = st.checkbox("Define system size in terms of feedstock mass [tonnes feedstock/hour].")
system_size_power_feedstock = st.checkbox("Define system size in terms of feedstock power/energy supply "
                                          "[MW feedstock LHV] or [MWh feedstock LHV/hour].")
system_size_power_electric = st.checkbox("Define system size in terms of net electric power [MWel].")

# Ensure at least one metric is given
if system_size_mass is False and system_size_power_feedstock is False and system_size_power_electric is False:
    st.error("ERROR: Please supply at least one system size metric.")
else:

    # Display user inputs
    if system_size_mass:
        system_size_mass_value = st.number_input(label="System size [tonnes feedstock/hour]", value=10.0, step=0.01)

    if system_size_power_feedstock:
        system_size_power_feedstock_value = st.number_input(label="System size [MW feedstock LHV] or [MWh feedstock LHV/hour]", value=10.0, step=0.01)

    if system_size_power_electric:
        system_size_power_electric_value = st.number_input(label="System size [MWel]", value=10.0, step=0.01)

    # Calculate estimates if required
    if not system_size_mass:
        if system_size_power_feedstock:
            system_size_mass_value = convert_system_size(value=system_size_power_feedstock_value,
                                                         input_units="MWh/hour",
                                                         feedstock_LHV=feedstock_LHV)["size_feedstock_mass"]
        else:
            system_size_mass_value = convert_system_size(value=system_size_power_electric_value,
                                                         input_units="MWel",
                                                         feedstock_LHV=feedstock_LHV)["size_feedstock_mass"]
            st.warning("Please note the system's size in terms of feedstock mass was estimated based on an empirical "
                       "relationship. This may be recalculated using a different method during the full simulation.")

    if not system_size_power_feedstock:
        if system_size_mass:
            system_size_power_feedstock_value = convert_system_size(value=system_size_mass_value,
                                                                    input_units="tonnes/hour",
                                                                    feedstock_LHV=feedstock_LHV)["size_feedstock_energy"]
        else:
            system_size_power_feedstock_value = convert_system_size(system_size_power_electric_value,
                                                                    input_units="MWel",
                                                                    feedstock_LHV=feedstock_LHV)["size_feedstock_energy"]
            st.warning("Please note the system's size in terms of feedstock energy was estimated based on an empirical "
                       "relationship. This may be recalculated using a different method during the full simulation.")

    if not system_size_power_electric:
        if system_size_mass:
            system_size_power_electric_value = convert_system_size(value=system_size_mass_value,
                                                                   input_units="tonnes/hour",
                                                                   feedstock_LHV=feedstock_LHV)["size_power"]
        else:
            system_size_power_electric_value = convert_system_size(value=system_size_power_feedstock_value,
                                                                   input_units="MWh/hour",
                                                                   feedstock_LHV=feedstock_LHV)["size_power"]
        st.warning("Please note the system's net electric power was estimated based on an empirical relationship. "
                   "This may be recalculated using a different method during the full simulation.")

    # Display estimated/given values.
    if system_size_mass is True or system_size_power_feedstock is True or system_size_power_electric is True:
        st.write("Your selected (or estimated) system size is:")
        st.write(f"{system_size_mass_value:.1f} [tonnes/hour]")
        st.write(f"{system_size_power_feedstock_value:.2f} [MW feedstock LHV] or [MWh feedstock LHV/hour]")
        st.write(f"{system_size_power_electric_value:.2f} [MWel]")

st.divider()

# %% Techno-economic analysis inputs
st.header("Techno-economic analysis choices")

st.subheader("General")
CEPCI_year = st.number_input("Select the year to which prices and costs should be updated to",
                             value=get_most_recent_available_CEPCI_year(),
                             step=1,
                             min_value=2001,
                             max_value=get_most_recent_available_CEPCI_year(),
                             help="During the simulations all prices and costs will be updated to this year using "
                                  "currency and cost index scaling. Generally the default year is the most recent "
                                  "CEPCI value.")
st.divider()

rate_of_return_percentage = st.number_input(label="Rate of return (or discount rate/interest rate) which is to be used "
                                                  "for economic analysis [%]",
                                            value=5.0,
                                            min_value=0.0,
                                            max_value=50.0,
                                            step=0.1,
                                            help="The rate of return is used to discount cash flows occurring at "
                                            "different times (e.g. convert an annuity to its present value "
                                            "equivalent.")
rate_of_return_decimals = rate_of_return_percentage / 100
st.divider()

st.subheader("Energy prices")
# Electricity price
electricity_price = st.selectbox(label=f"Select the electricity wholesale price [{currency}/kWh]",
                                 options=economic_inputs_options)
electricity_price_parameters = {}
if electricity_price == "user selected":
    electricity_price_user_selected = st.radio(label="Distribution type", options=distribution_options, index=0,
                                               key="electricity price distribution type")
    electricity_price_parameters = display_correct_user_distribution_inputs(choice=electricity_price_user_selected,
                                                                            key="electricity price distribution " +
                                                                                electricity_price_user_selected,
                                                                            step_size="any")
    st.divider()
else:
    st.divider()

# Heat/thermal energy price
heat_price = st.selectbox(label=f"Select the heat/thermal energy wholesale price [{currency}/kWh]",
                          options=economic_inputs_options)
heat_price_parameters = {}
if heat_price == "user selected":
    heat_price_user_selected = st.radio(label="Distribution type", options=distribution_options, index=0,
                                        key="heat price distribution type")
    heat_price_parameters = display_correct_user_distribution_inputs(choice=heat_price_user_selected,
                                                                     key="heat price distribution " +
                                                                         heat_price_user_selected,
                                                                     step_size="any")
    st.divider()
else:
    st.divider()

# Biochar price
st.subheader("Biochar price")
biochar_price = st.selectbox(label=f"Select the biochar price [{currency}/tonne]",
                             options=economic_inputs_options,
                             index=1,
                             help="Biochar prices can vary greatly based on local conditions. "
                                  "User selected values are recommended.")
biochar_price_parameters = {}
if biochar_price == "user selected":
    biochar_price_user_selected = st.radio(label="Distribution type", options=distribution_options, index=0,
                                           key="biochar price distribution type")
    biochar_price_parameters = display_correct_user_distribution_inputs(choice=biochar_price_user_selected,
                                                                        key="biochar price distribution " +
                                                                            biochar_price_user_selected)
    st.divider()
else:
    st.divider()

# Gate fee/feedstock cost
st.subheader("Gate fee/feedstock cost")
gate_fee_feedstock_price_selector = st.selectbox(label="Select whether a gate fee will be received for treating the "
                                                       "feedstock or the feedstock will need to be bought.",
                                                 options=["gate fee", "feedstock cost"])

gate_fee_feedstock_price = st.selectbox(label=f"Select the {gate_fee_feedstock_price_selector} [{currency}/tonne]",
                                        options=economic_inputs_options,
                                        index=1,
                                        help="As this can drastically vary based on local conditions user "
                                             "selected values are recommended.")

if gate_fee_feedstock_price == "default":
    st.error("Currently default values are not supported for gate fees/feedstock costs, because these vary "
             "too much based on the feedstock choice and regional conditions etc.")

gate_fee_feedstock_price_parameters = {}
if gate_fee_feedstock_price == "user selected":
    gate_fee_feedstock_price_user_selected = st.radio(label="Distribution type", options=distribution_options, index=0,
                                                      key="gate fee or feedstock price distribution type")
    gate_fee_feedstock_price_parameters = display_correct_user_distribution_inputs(
        choice=gate_fee_feedstock_price_user_selected,
        key="gate fee or feedstock price distribution" + gate_fee_feedstock_price_user_selected)
    st.divider()
else:
    st.divider()

# Carbon tax
st.subheader("Carbon tax")
carbon_tax_selector = st.checkbox("Is a carbon tax to be considered?")

# Initialise defaults
carbon_tax = None
carbon_tax_parameters = {}

if carbon_tax_selector:
    carbon_tax = st.selectbox(label=f"Select the carbon tax [{currency}/tonne CO2eq.]",
                              options=economic_inputs_options,
                              index=1,
                              help="A carbon tax or potential carbon tax are subject to frequent changes. "
                                   "User selected values are recommended.")

    if carbon_tax == "user selected":
        carbon_tax_user_selected = st.radio(label="Distribution type", options=distribution_options, index=0,
                                            key="carbon tax distribution type")
        carbon_tax_parameters = display_correct_user_distribution_inputs(choice=carbon_tax_user_selected,
                                                                         key="carbon tax distribution " +
                                                                             carbon_tax_user_selected)
        st.divider()
    else:
        st.divider()
else:
    st.divider()

st.subheader("Carbon capture and storage (CCS)")
carbon_capture_included_1 = st.checkbox(label="Is carbon capture and storage included?", value=False,
                                        key="carbon_capture_included_1")

# Initialise defaults
CO2_transport_price = None
CO2_storage_price = None
CO2_transport_parameters = {}
CO2_storage_parameters = {}

if carbon_capture_included_1:
    CO2_transport_price = st.selectbox(label=f"Select the CO2 transport price [{currency}/tonne CO2]",
                                       options=economic_inputs_options,
                                       index=1,
                                       help="CO2 transport costs vary greatly depending on the transport method and "
                                            "distance. User selected values are recommended.")

    if CO2_transport_price == "user selected":
        CO2_transport_price_user_selected = st.radio(label="Distribution type", options=distribution_options, index=0,
                                                     key="CO2 transport price distribution type")
        CO2_transport_parameters = display_correct_user_distribution_inputs(choice=CO2_transport_price_user_selected,
                                                                            key="CO2 transport price distribution " +
                                                                                CO2_transport_price_user_selected)
        st.divider()
    else:
        st.divider()

    CO2_storage_price = st.selectbox(label=f"Select the CO2 storage price [{currency}/tonne CO2]",
                                     options=economic_inputs_options,
                                     index=1,
                                     help="CO2 storage costs vary greatly depending on the locally available storage "
                                          "options. User selected values are recommended.")

    if CO2_storage_price == "user selected":
        CO2_storage_price_user_selected = st.radio(label="Distribution type", options=distribution_options, index=0,
                                                   key="CO2 storage price distribution type")
        CO2_storage_parameters = display_correct_user_distribution_inputs(choice=CO2_storage_price_user_selected,
                                                                          key="CO2 storage price distribution " +
                                                                              CO2_storage_price_user_selected)
        st.divider()
    else:
        st.divider()

else:
    st.divider()

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
    biochar_additional_inputs = st.checkbox(label="Display additional biochar inputs",
                                            value=False, key="biochar_additional_inputs")
    if biochar_additional_inputs:
        st.write("A number of parameters regarding the biochar's yield and composition can be updated here if known.")
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
carbon_capture_included_2 = st.checkbox(label="Select to include CCS", value=carbon_capture_included_1,
                                        key="carbon_capture_included_2")
carbon_capture_method = None  # set default

if carbon_capture_included_2:
    carbon_capture_method = st.radio(label="Display additional inputs", options=carbon_capture_options)
    if carbon_capture_method == "Vacuum pressure swing adsorption (VPSA) post combustion capture (default)":
        carbon_capture_method = "VPSA post combustion"
    elif carbon_capture_method == "Amine-based post combustion capture":
        carbon_capture_method = "Amine post comb"

# %% Combined heat and power (CHP) plant
st.subheader("Optional user inputs")
CHP_display_additional_inputs = st.checkbox(label="Display additional combined heat and power (CHP) inputs",
                                            value=False, key="CHP_additional_inputs")
CHP_dict = {}
if CHP_display_additional_inputs:
    CHP_unit = st.radio(label="Display additional inputs", options=CHP_options)
    # Set defaults
    CHP_electrical_efficiency = None
    CHP_thermal_efficiency = None
    CHP_parasitic_energy_demand = None
    CHP_size_kW = None
    if CHP_unit == "User defined":
        CHP_electrical_efficiency = st.number_input(label="Electrical efficiency as a decimal", value=float(0),
                                                    min_value=float(0), max_value=float(1))
        CHP_thermal_efficiency = st.number_input(label="Thermal efficiency as a decimal",  value=float(0),
                                                 min_value=float(0), max_value=float(1))
        CHP_parasitic_energy_demand = st.number_input(label="Parasitic energy demand as a decimal", value=float(0),
                                                      min_value=float(0), max_value=float(1))
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
                            "currency": currency,
                            "system_life_span": system_life_span,
                            "annual_operating_hours_user_imputed": annual_operating_hours_check,
                            "annual_operating_hours": annual_operating_hours_value
                            },

                "feedstock": {"category": feedstock_category,  # general
                              "name": feedstock_name,
                              "biogenic_carbon_fraction": biogenic_carbon_fraction,
                              "particle_size_ar": particle_size_ar,
                              "carbon": feedstock_C,  # ultimate composition
                              "hydrogen": feedstock_H,
                              "nitrogen": feedstock_N,
                              "sulphur": feedstock_S,
                              "oxygen": feedstock_O,
                              "LHV": feedstock_LHV,
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
                "system_size": {"mass_basis_user_imputed": system_size_mass,
                                "power_feedstock_user_imputed": system_size_power_feedstock,
                                "power_electric_user_imputed": system_size_power_electric,
                                "mass_basis_tonnes_per_hour": system_size_mass_value,
                                "power_feedstock_MW_feedstock_LHV": system_size_power_feedstock_value,
                                "power_electric_MW_el": system_size_power_electric_value
                                },

                "economic": {"CEPCI_year": CEPCI_year,
                             "rate_of_return_decimals": rate_of_return_decimals,
                             "electricity_price_choice": electricity_price,
                             "electricity_price_parameters": electricity_price_parameters,
                             "heat_price_choice": heat_price,
                             "heat_price_parameters": heat_price_parameters,
                             "biochar_price_choice": biochar_price,
                             "biochar_price_parameters": biochar_price_parameters,
                             "gate_fee_or_feedstock_price_selection": gate_fee_feedstock_price_selector,
                             "gate_fee_or_feedstock_price_choice": gate_fee_feedstock_price,
                             "gate_fee_or_feedstock_price_parameters": gate_fee_feedstock_price_parameters,
                             "carbon_tax_included": carbon_tax_selector,
                             "carbon_tax_choice": carbon_tax,
                             "carbon_tax_parameters": carbon_tax_parameters,
                             "CO2_transport_price_choice": CO2_transport_price,
                             "CO2_transport_price_parameters": CO2_transport_parameters,
                             "CO2_storage_price_choice": CO2_storage_price,
                             "CO2_storage_price_parameters": CO2_storage_parameters
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
                    "carbon_capture": {"included": carbon_capture_included_2,
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
