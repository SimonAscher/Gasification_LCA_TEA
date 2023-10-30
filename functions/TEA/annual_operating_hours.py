import os

import pandas as pd
import numpy as np

import functions


def get_annual_operating_hours_draws():
    """
    Get distribution draws of annual operating hours based on empirical model.

    Returns
    -------
    list
        Distribution draws [hours/year].
    """
    from objects import triangular_dist_maker  # import here to avoid circular import error

    # Load and display data
    root_dir = functions.general.utility.get_project_root()

    data_file = "annual_operating_hours.csv"
    data_file_path = os.path.join(root_dir, "data", data_file)
    df_source = pd.read_csv(data_file_path)
    df = df_source.copy()  # working copy of original dataframe

    # Hours before rejecting outliers
    hours_array_raw = np.array(df["Value"])
    # Hours after rejecting outliers
    hours_array_after_rejecting_outliers = functions.general.utility.reject_outliers(hours_array_raw, 2)

    # Define and get distribution draws
    dist_maker = triangular_dist_maker(lower=hours_array_after_rejecting_outliers.min(),
                                       mode=np.mean(hours_array_after_rejecting_outliers),
                                       upper=hours_array_after_rejecting_outliers.max())

    distribution = list(functions.MonteCarloSimulation.get_distribution_draws(distribution_maker=dist_maker))

    return distribution
