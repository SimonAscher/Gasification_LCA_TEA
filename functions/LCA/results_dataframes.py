import pandas as pd
import numpy as np
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
    GWP_inc_biogenic = []
    subprocess_names = []
    subprocess_GWP = []
    units = []

    # Get data for storage in dataframe
    for count in list(range(settings.background.iterations_MC)):
        process_name.append(process_GWP_output_MC.simulation_results[count].process_name)
        GWP.append(process_GWP_output_MC.simulation_results[count].GWP)
        GWP_inc_biogenic.append(process_GWP_output_MC.simulation_results[count].GWP_inc_biogenic)
        subprocess_names.append(process_GWP_output_MC.simulation_results[count].subprocess_names)
        subprocess_GWP.append(process_GWP_output_MC.simulation_results[count].subprocess_GWP)
        units.append(process_GWP_output_MC.simulation_results[count].units)

    # Store data in dataframe
    df.loc["process_name", df.columns[0]] = process_name
    df.loc["GWP", df.columns[0]] = GWP
    df.loc["GWP_inc_biogenic", df.columns[0]] = GWP_inc_biogenic
    df.loc["subprocess_names", df.columns[0]] = subprocess_names
    df.loc["subprocess_GWP", df.columns[0]] = subprocess_GWP
    df.loc["units", df.columns[0]] = units
    df.loc["subprocess_abbreviations", df.columns[0]] = process_GWP_output_MC.subprocess_abbreviations  # populate

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
