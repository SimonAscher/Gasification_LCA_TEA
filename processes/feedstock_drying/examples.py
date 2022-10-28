from processes.feedstock_drying import energy_drying, drying_GWP, drying_GWP_MC

mass = 1000  # [kg]
moist_ar = 20  # moisture content as a fraction of feedstock on an as received basis
moist_post = 12  # desired final moisture content as a fraction

energy_drying_output_default = energy_drying(mass_feedstock=mass, moisture_ar=moist_ar,
                                             moisture_post_drying=moist_post,
                                             dryer_type='Direct fired dryer',
                                             specific_heat_reference_temp='40 degC',
                                             electricity_reference='GaBi (mean)',
                                             output_unit='kWh', syngas_as_fuel=False, show_values=False)

energy_drying_output = energy_drying(dryer_type='Direct fired dryer',
                                     specific_heat_reference_temp='40 degC', electricity_reference='GaBi (mean)',
                                     output_unit='kWh', syngas_as_fuel=False, show_values=False)

GWP_drying_default = drying_GWP(energy_drying_output_default)
GWP_drying = drying_GWP(energy_drying_output)


# Monte Carlo
MC_example = drying_GWP_MC()
