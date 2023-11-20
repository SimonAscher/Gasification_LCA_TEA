from config import settings
from processes.CHP import CombinedHeatPower
from processes.gasification import Gasification
from processes.syngas_combustion import SyngasCombustion
from processes.biochar_soil_application import BiocharSoilApplication
from processes.carbon_capture import CarbonCapture
from processes.pretreatment import (FeedstockDrying, FeedstockPelleting, FeedstockMilling, FeedstockBaleShredding,
                                    Pretreatment)
from objects.result_objects import Results


def run_simulation():
    # Create processes
    processes = ()  # to store all created processes

    # Pretreatment - Note: Run first so that particle size gets updated
    process_pretreatment = None
    if settings.user_inputs.processes.drying.included or settings.user_inputs.processes.milling.included or settings.user_inputs.processes.pelleting.included or settings.user_inputs.processes.bale_shredding.included:
        process_pretreatment = Pretreatment()

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

    # Syngas combustion and CHP
    process_CHP = CombinedHeatPower()
    process_syngas_combustion = SyngasCombustion()
    process_CHP.add_subprocess(process_syngas_combustion)  # add subprocess
    processes = processes + (process_CHP,)

    # Biochar application to soil
    if settings.user_inputs.processes.biochar.included:
        process_biochar = BiocharSoilApplication(short_label="Biochar")
        processes = processes + (process_biochar,)

    # Carbon Capture
    if settings.user_inputs.processes.carbon_capture.included:
        process_carbon_capture = CarbonCapture(instantiate_with_default_reqs=False)
        # Calculate requirements and GWP/TEA manually to avoid rerunning syngas combustion sub-model
        process_carbon_capture.calculate_requirements(syngas_combustion_object=process_syngas_combustion,
                                                      cc_method=settings.user_inputs.processes.carbon_capture.method)
        process_carbon_capture.calculate_GWP()
        process_carbon_capture.calculate_TEA()
        processes = processes + (process_carbon_capture,)

    # Create results object
    results = Results(processes=processes, plot_style="digital")
    results.calculate_total_GWP()
    results.calculate_global_economic_effects()
    results.calculate_total_TEA()
    results.calculate_electricity_heat_output()

    # # Plot results
    results.plot_all_results()

    return results
