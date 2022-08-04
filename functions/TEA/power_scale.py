def power_scale(baseline_size: float, design_size: float, baseline_cost: float, scaling_factor: float = 0.7) -> float:
    """
    Power scaling method used to scale the capital cost (CAPEX) of a designed plant based on the cost of a reference
    plant.

    Parameters
    ----------
    baseline_size: float
        Baseline size of plant in e.g. kW, tonnes per day, etc.
    design_size: float
        Size of designed plant - ensure same units used as for baseline_size
    baseline_cost: float
        Baseline cost of plant
    scaling_factor: float
        Scaling factor to be used in power scaling technique - also see note for more information

    Returns
    -------
    float
        Plant capital cost after power scaling

    .. note::
    Default scaling factor (f) is 0.7, but more linear relationship identified in e.g. Angelonidi & Smith (2015).
    """

    scaled_cost = baseline_cost * ((design_size / baseline_size) ** scaling_factor)

    return scaled_cost
