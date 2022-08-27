import numpy as np

# Create and employ sub-function to scale gas fractions so they sum up to 100 %
def scale_gas_fractions1(gas_fractions, ):
    '''
    Scales gas fractions so they sum up to 100 %.
    '''

    # Set up empty list to store scaled arrays
    N2 = []
    H2 = []
    CO = []
    CO2 = []
    CH4 = []
    C2H4 = []

    # Loop through each Monte Carlo sample
    for iterations in np.arange(len(gas_fractions['N2'])):

        elements = []  # empty list to store different gas species for each iteration
        keys = list(gas_fractions)  # get list of keys of gas_fractions dictionary

        # Loop through gas species
        for species in np.arange(len(gas_fractions)):  # extract different gas species for each Monte Carlo iteration
            elements.append(gas_fractions[keys[species]][iterations])

        # Scale and update values. Note: Turned into decimals now.
        N2.append(elements[0] * (100 / sum(elements)) / 100)
        H2.append(elements[1] * (100 / sum(elements)) / 100)
        CO.append(elements[2] * (100 / sum(elements)) / 100)
        CO2.append(elements[3] * (100 / sum(elements)) / 100)
        CH4.append(elements[4] * (100 / sum(elements)) / 100)
        C2H4.append(elements[5] * (100 / sum(elements)) / 100)

    # Create new dictionary with scaled values
    scaled_gas_fractions = {'N2': N2, 'H2': H2, 'CO': CO, 'CO2': CO2, 'CH4': CH4, 'C2H4': C2H4}
    return scaled_gas_fractions

gas_pred = {'N2':[50, 40, 45], 'H2':[12, 9, 14], 'CO':[14, 12, 14], 'CO2':[10, 12, 14], 'CH4':[5, 4, 3], 'C2H4':[1, 1, 2]}
gas_pred1 = [40, 30, 20, 10]

test1 = scale_gas_fractions1(gas_pred)
test2 = scale_gas_fractions1(gas_pred1)
from functions.general.utility import scale_gas_fractions



