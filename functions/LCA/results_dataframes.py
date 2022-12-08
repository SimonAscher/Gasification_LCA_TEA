import numpy as np
import pandas as pd

from config import settings


def process_GWP_MC_to_df(process_GWP_output_MC):
    """
    Turns a process' process_GWP_output_MC object into a pandas dataframe.

    Parameters
    ----------
    process_GWP_output_MC: object
        process_GWP_output_MC object containing the results of a process' Monte Carlo LCA results.

    Returns
    -------
    pd.DataFrame
    """
    # Initialise dataframe
    df = pd.DataFrame(index=list(process_GWP_output_MC.simulation_results[0].__annotations__),
                      columns=[process_GWP_output_MC.process_name])

    # Add subprocess abbreviations to dataframe
    df = pd.concat((df, pd.DataFrame(columns=(df.columns[0],), index=("subprocess_abbreviations",))))

    # Initialise lists to store extracted data
    process_name = []
    GWP = []
    GWP_from_biogenic = []
    subprocess_names = []
    subprocess_GWP = []
    units = []

    # Get data for storage in dataframe
    for count in list(range(settings.background.iterations_MC)):
        process_name.append(process_GWP_output_MC.simulation_results[count].process_name)
        GWP.append(process_GWP_output_MC.simulation_results[count].GWP)
        GWP_from_biogenic.append(process_GWP_output_MC.simulation_results[count].GWP_from_biogenic)
        subprocess_names.append(process_GWP_output_MC.simulation_results[count].subprocess_names)
        subprocess_GWP.append(process_GWP_output_MC.simulation_results[count].subprocess_GWP)
        units.append(process_GWP_output_MC.simulation_results[count].units)

    # Store data in dataframe
    df.loc["process_name", df.columns[0]] = process_name
    df.loc["GWP", df.columns[0]] = GWP
    df.loc["GWP_from_biogenic", df.columns[0]] = GWP_from_biogenic
    df.loc["subprocess_names", df.columns[0]] = subprocess_names
    df.loc["subprocess_GWP", df.columns[0]] = subprocess_GWP
    df.loc["units", df.columns[0]] = units
    df.loc["subprocess_abbreviations", df.columns[0]] = process_GWP_output_MC.subprocess_abbreviations

    return df


def absorb_process_df(master_df, absorbed_df, new_process_name=None, abbreviation_absorbed_process=None, absorb_subprocesses=True):
    """
    Absorb the MC GWP results dataframe of one process into the one of another (i.e. combine two processes into one).

    Parameters
    ----------
    master_df: pd.DataFrame
        Main dataframe which will absorb the other one.
    absorbed_df: pd.DataFrame
        Dataframe which is to be absorbed.
    new_process_name: str
        If given overwrites the process name. If not given name from master_df taken.
    abbreviation_absorbed_process: str
        Abbreviation label for absorbed process.
    absorb_subprocesses: bool
        Indicates whether subprocess in absorbed dataframe should be compressed into one process (False) or
        maintained (True).

    Returns
    -------
    pd.DataFrame
        Updated master dataframe after absorbing other dataframe.
    """

    # Get defaults
    if abbreviation_absorbed_process is None:
        abbreviation_absorbed_process = absorbed_df.columns[0]  # Use full name if no abbreviated name given

    # Initialise dataframe
    if isinstance(new_process_name, str):
        df = pd.DataFrame(index=master_df.index, columns=[new_process_name])
    else:
        df = pd.DataFrame(index=master_df.index, columns=[master_df.columns[0]])


    # Initialise lists to store extracted data

    # Master df
    process_name_master = []
    GWP_master = []
    GWP_from_biogenic_master = []
    subprocess_names_master = []
    subprocess_GWP_master = []
    units_master = []

    # Absorbed df
    GWP_absorbed = []
    GWP_from_biogenic_absorbed = []
    subprocess_names_absorbed = []
    subprocess_GWP_absorbed = []
    units_absorbed = []

    # Get data for storage in dataframe
    for count in list(range(settings.background.iterations_MC)):
        # Master df
        if isinstance(new_process_name, str):
            process_name_master.append(new_process_name)
        else:
            process_name_master.append(master_df.loc["process_name"][master_df.columns[0]][count])
        GWP_master.append(master_df.loc["GWP"][master_df.columns[0]][count])
        GWP_from_biogenic_master.append(master_df.loc["GWP_from_biogenic"][master_df.columns[0]][count])
        subprocess_names_master.append(master_df.loc["subprocess_names"][master_df.columns[0]][count])
        subprocess_GWP_master.append(master_df.loc["subprocess_GWP"][master_df.columns[0]][count])
        units_master.append(master_df.loc["units"][master_df.columns[0]][count])

        # Absorbed df
        current_process_name_absorbed = absorbed_df.loc["process_name"][absorbed_df.columns[0]][count]
        GWP_absorbed.append(absorbed_df.loc["GWP"][absorbed_df.columns[0]][count])
        GWP_from_biogenic_absorbed.append(absorbed_df.loc["GWP_from_biogenic"][absorbed_df.columns[0]][count])
        process_names = (current_process_name_absorbed + " ",) * len(
            absorbed_df.loc["subprocess_names"][absorbed_df.columns[0]][
                count])  # create tuple to indicate subprocess belongs to absorbed process
        subprocess_names_absorbed.append(tuple(
            map(lambda x, y: x + y, process_names, absorbed_df.loc["subprocess_names"][absorbed_df.columns[0]][count])))
        subprocess_GWP_absorbed.append(absorbed_df.loc["subprocess_GWP"][absorbed_df.columns[0]][count])
        units_absorbed.append(absorbed_df.loc["units"][absorbed_df.columns[0]][count])

    # Ascertain that units match
    if units_absorbed != units_master:
        raise ValueError("Units of to be combined dataframes do not match.")

    # Get parameters to be stored in final df
    process_name_combined = process_name_master
    GWP_combined = list(np.array(GWP_master) + np.array(GWP_absorbed))
    GWP_from_biogenic_combined = list(np.array(GWP_from_biogenic_master) + np.array(GWP_from_biogenic_absorbed))
    subprocess_names_combined = list(map(lambda x, y: x + y, subprocess_names_master, subprocess_names_absorbed))
    subprocess_GWP_combined = list(map(lambda x, y: x + y, subprocess_GWP_master, subprocess_GWP_absorbed))
    units_combined = units_master

    if absorb_subprocesses:
        subprocess_names_combined = list(map(lambda x, y: x + y, subprocess_names_master, subprocess_names_absorbed))
        subprocess_GWP_combined = list(map(lambda x, y: x + y, subprocess_GWP_master, subprocess_GWP_absorbed))

        absorbed_process_name_abbreviations = (abbreviation_absorbed_process + " ",) * len(
            absorbed_df.loc["subprocess_abbreviations"][
                absorbed_df.columns[0]])  # create tuple to indicate subprocess belongs to absorbed process
        subprocess_abbreviations_combined = master_df.loc["subprocess_abbreviations"][master_df.columns[0]] + tuple(
            map(lambda x, y: x + y, absorbed_process_name_abbreviations,
                absorbed_df.loc["subprocess_abbreviations"][absorbed_df.columns[0]]))
    else:
        # TODO: Add case where subprocess' get all compressed to one name, abbreviation, and GWP value.
        pass

    # Store data in dataframe
    df.loc["process_name", df.columns[0]] = process_name_combined
    df.loc["GWP", df.columns[0]] = GWP_combined
    df.loc["GWP_from_biogenic", df.columns[0]] = GWP_from_biogenic_combined
    df.loc["subprocess_names", df.columns[0]] = subprocess_names_combined
    df.loc["subprocess_GWP", df.columns[0]] = subprocess_GWP_combined
    df.loc["units", df.columns[0]] = units_combined
    df.loc["subprocess_abbreviations", df.columns[0]] = subprocess_abbreviations_combined

    return df


def combine_GWP_dfs(dataframes):
    """
    Combines all process dataframes and calculates the overall GWP of the system.
    Parameters
    ----------
    dataframes: tuple[pd.DataFrame]
        Dataframes of each considered process.

    Returns
    -------
    pd.DataFrame
        Summary dataframe combining LCA calculations for all processes. Used in plotting functions.

    """
    # Create new dataframe by combining all smaller dataframes
    combined_df = pd.concat(dataframes, axis=1)

    # Add total/overall GWP to dataframe
    all_GWPs = []
    for count, _ in enumerate(list(dataframes)):
        all_GWPs.append(combined_df.loc["GWP", combined_df.columns[count]])

    # Add total of all GWPs to dataframe
    combined_df["Total"] = np.nan  # Initialise new column
    combined_df["Total"] = combined_df["Total"].astype('object')  # Turn column into correct type
    combined_df.at["GWP", "Total"] = list(sum(map(np.array, all_GWPs)))  # Calculate totals and store in dataframe

    return combined_df


def get_GWP_summary_df(processes):
    """
    Wrapper/convenience function that uses process_GWP_MC_to_df and combine_GWP_df to get final GWP MC analysis dataframe.

    Parameters
    ----------
    processes
        TODO: Should work by taking an input ~ like this: considered_processes = ("Drying", "Gasification", "CHP")

    Returns
    -------

    """
