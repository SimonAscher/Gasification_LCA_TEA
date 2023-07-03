import numpy as np

from config import settings
from processes.CHP import CombinedHeatPower
from processes.gasification import Gasification
from processes.syngas_combustion import SyngasCombustion
from processes.biochar_soil_application import BiocharSoilApplication
from processes.carbon_capture import CarbonCapture
from processes.pretreatment import FeedstockDrying, FeedstockPelleting, FeedstockMilling, FeedstockBaleShredding
from objects.result_objects import Results
from objects import Process
from functions.LCA import electricity_GWP, thermal_energy_GWP

def run_LCA():
    # Create processes
    processes = ()  # to store all created processes

    # Pretreatment
    # Note: Run first so that particle size gets updated
    process_pretreatment = None
    if settings.user_inputs.processes.drying.included or settings.user_inputs.processes.milling.included or settings.user_inputs.processes.pelleting.included or settings.user_inputs.processes.bale_shredding.included:
        process_pretreatment = Process(name="Pretreatment", short_label="Pre.", instantiate_with_default_reqs=False)

        if settings.user_inputs.processes.drying.included:
            process_pretreatment.add_subprocess(FeedstockDrying())

        if settings.user_inputs.processes.milling.included:
            process_pretreatment.add_subprocess(FeedstockMilling())

        if settings.user_inputs.processes.pelleting.included:
            process_pretreatment.add_subprocess(FeedstockPelleting())

        if settings.user_inputs.processes.bale_shredding.included:
            process_pretreatment.add_subprocess(FeedstockBaleShredding())

        processes = processes + (process_pretreatment,)

    # Gasification
    process_gasification = Gasification(short_label="Gasif.")
    processes = processes + (process_gasification,)

    # CHP
    process_CHP = CombinedHeatPower()
    process_syngas_combustion = SyngasCombustion()
    process_CHP.add_subprocess(process_syngas_combustion)  # add subprocess
    processes = processes + (process_CHP,)

    # Carbon Capture
    if settings.user_inputs.processes.carbon_capture.included:
        process_carbon_capture = CarbonCapture(instantiate_with_default_reqs=False)
        process_carbon_capture.calculate_requirements(syngas_combustion_object=process_syngas_combustion,
                                                      cc_method=settings.user_inputs.processes.carbon_capture.method)
        process_carbon_capture.calculate_GWP()
        process_carbon_capture.calculate_TEA()
        processes = processes + (process_carbon_capture,)

    # Biochar
    if settings.user_inputs.processes.biochar.included:
        process_biochar = BiocharSoilApplication(short_label="Biochar.")
        processes = processes + (process_biochar,)
        process_biochar.plot_GWP()

    # Plot individual processes
    process_CHP.update_plot_style(style="poster")
    process_CHP.plot_GWP()
    try:
        process_pretreatment.update_plot_style(style="poster")
        process_pretreatment.plot_GWP()
    except:
        pass

    # Results object
    example_results = Results(processes=processes, plot_style="digital")
    example_results.calculate_total_GWP()
    example_results.calculate_electricity_heat_output()

    # # Plot results
    example_results.save_report(storage_path=r"C:\Users\2270577A\OneDrive - University of Glasgow\Desktop\LCA_report",
                                save_figures=True)
    example_results.save_streamlit_report()

    return example_results
