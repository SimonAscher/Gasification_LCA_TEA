import numpy as np


def scale_gas_fractions(gas_fractions, gas_fractions_format="decimals"):
    """
    Scales gas fractions, so they sum up to 100 %.

    Parameters
    ----------
    gas_fractions: dict or np.array[float]
        Array of gas fractions which are to be scaled
    gas_fractions_format: str
        Specifies whether the gas fractions are given as decimals or percentages
    Returns
    -------
    np.array[float] or dict
        Array of scaled gas fractions or dict of scaled gas fractions in decimals.

    """
    # Check that data is given in correct length
    if len(gas_fractions) != 6:
        raise ValueError(f"gas_fractions needs to be length 6, is {len(gas_fractions)}")

    # More complex case where data is given in dictionary - note supports multiple entries in dictionary.
    if isinstance(gas_fractions, dict):

        # Set up empty list to store scaled arrays
        N2 = []
        H2 = []
        CO = []
        CO2 = []
        CH4 = []
        C2H4 = []

        # Loop through each Monte Carlo sample
        for iterations in np.arange(len(gas_fractions[list(gas_fractions)[0]])):

            elements = []  # empty list to store different gas species for each iteration
            keys = list(gas_fractions)  # get list of keys of gas_fractions dictionary

            # Loop through gas species
            for species in np.arange(
                    len(gas_fractions)):  # extract different gas species for each Monte Carlo iteration
                elements.append(gas_fractions[keys[species]][iterations])

            # Check in which format data is provided and scale and update accordingly
            if gas_fractions_format == "percentages":
                N2.append(elements[0] * (100 / sum(elements)) / 100)
                H2.append(elements[1] * (100 / sum(elements)) / 100)
                CO.append(elements[2] * (100 / sum(elements)) / 100)
                CO2.append(elements[3] * (100 / sum(elements)) / 100)
                CH4.append(elements[4] * (100 / sum(elements)) / 100)
                C2H4.append(elements[5] * (100 / sum(elements)) / 100)

            elif gas_fractions_format == "decimals":
                N2.append(elements[0] * (100 / sum(elements)))
                H2.append(elements[1] * (100 / sum(elements)))
                CO.append(elements[2] * (100 / sum(elements)))
                CO2.append(elements[3] * (100 / sum(elements)))
                CH4.append(elements[4] * (100 / sum(elements)))
                C2H4.append(elements[5] * (100 / sum(elements)))

            else:
                print("Check whether gas fractions have been provided in right format")

        # Create new dictionary with scaled values
        scaled_gas_fractions = {'N2 [vol.% db]': N2, 'H2 [vol.% db]': H2, 'CO [vol.% db]': CO, 'CO2 [vol.% db]': CO2,
                                'CH4 [vol.% db]': CH4, 'C2Hn [vol.% db]': C2H4}

    # Simpler case where data is given in an array
    else:
        unscaled_total = sum(gas_fractions)

        if gas_fractions_format == "percentages":
            scaled_gas_fractions = gas_fractions * (100 / unscaled_total) / 100

        elif gas_fractions_format == "decimals":
            scaled_gas_fractions = gas_fractions * (1 / unscaled_total)

        else:
            print("Check whether gas fractions have been provided in right format")

    return scaled_gas_fractions
