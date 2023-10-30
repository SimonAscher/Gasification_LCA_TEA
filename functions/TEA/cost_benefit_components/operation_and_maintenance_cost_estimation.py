import functions

import numpy as np

from objects import fixed_dist_maker, gaussian_dist_maker, triangular_dist_maker, range_dist_maker


def get_operation_and_maintenance_cost(CAPEX_values, o_and_m_ratio_dist_maker=None):
    """
    Calculates the annual operation and maintenance cost of a process based on its CAPEX.

    Parameters
    ----------
    CAPEX_values: list[float]
        List of present value CAPEX draws.
    o_and_m_ratio_dist_maker: fixed_dist_maker | gaussian_dist_maker | triangular_dist_maker | range_dist_maker
        Distribution maker defining the ratio between operation and maintenance cost and CAPEX.

    Returns
    -------
    list[float]
        Annual operation and maintenance cost.
    """
    # Convert to annual operation and maintenance cost
    if o_and_m_ratio_dist_maker is None:
        o_and_m_ratio_dist_maker = triangular_dist_maker(0.02, 0.04, 0.07)  # Fixed O&M cost as fraction of CAPEX
        # Based on analysis done in operation_and_maintenance_cost_fraction.ipynb

    o_and_m_ratio_distribution = functions.MonteCarloSimulation.get_distribution_draws(o_and_m_ratio_dist_maker)

    annual_o_and_m_cost = list(np.multiply(CAPEX_values, o_and_m_ratio_distribution))

    # Raise error if values are not given as decimals.
    if o_and_m_ratio_dist_maker is not None and o_and_m_ratio_dist_maker[0] > 1:
        raise ValueError("Distribution values should be given as decimals.")

    return annual_o_and_m_cost
