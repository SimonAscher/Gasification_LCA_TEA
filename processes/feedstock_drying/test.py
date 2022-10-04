from processes.feedstock_drying import energy_drying, drying_GWP

mass_feedstock = 1000  # [kg]
moisture_ar = 0.20  # moisture content as a fraction of feedstock on an as received basis
moisture_post_drying = 0.12  # desired final moisture content as a fraction

energy_drying_output = energy_drying(mass_feedstock, moisture_ar, moisture_post_drying, dryer_type='Direct fired dryer',
                                     specific_heat_reference_temp='40 degC', electricity_reference='GaBi (mean)',
                                     output_unit='kWh', syngas_as_fuel=False, show_values=True)

GWP_drying = drying_GWP(energy_drying_output)

