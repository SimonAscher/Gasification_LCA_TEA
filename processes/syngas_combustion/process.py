def syngas_combustion_GWP(gas_predictions):
    '''
    Function used to calculate the GWP of syngas combustion.
    '''

    # Define densities of different gas species # Note: Should not be requried as already previously defined. Change name if I decide to store information such as densities in a dataframe at later stage etc.
    # densities = densities

    # Extract gas_yield for later use
    gas_yield = gas_predictions['Yield']

    # Create dictionary of gas species only
    gas_fractions = gas_predictions.copy()
    # Drop unrequired variables if they exist in dictionary:
    if 'LHV' in gas_fractions:
        gas_fractions.pop('LHV')
    if 'Yield' in gas_fractions:
        gas_fractions.pop('Yield')

    # Create and employ sub-function to scale gas fractions so they sum up to 100 %
    def scale_gas_fractions(gas_fractions):
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
            for species in np.arange(
                    len(gas_fractions)):  # extract different gas species for each Monte Carlo iteration
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

    # Employ scaling function
    scaled_gas_fractions = scale_gas_fractions(gas_fractions)

    # Create and employ sub-function to calculate GWP of syngas combustion
    def syngas_combustion_CO2_eq(scaled_gas_fractions, gas_yield):
        '''
        Sub-function used to calculate the GWP from syngas combustion.
        Simplified function assuming complete conversion of all species to CO2.
        '''

        # Set up empty list to store caluclated GWPs
        GWP = []

        # Calculate GWPs for each MC iteration
        for iterations in np.arange(len(gas_fractions['N2'])):
            calculated_GWP = (scaled_gas_fractions['CO2'][iterations] + \
                              scaled_gas_fractions['CO'][iterations] * (densities['CO2'] / densities['CO']) + \
                              scaled_gas_fractions['CH4'][iterations] * (densities['CO2'] / densities['CH4']) + \
                              scaled_gas_fractions['C2H4'][iterations] * (densities['CO2'] / densities['C2H4'])) * \
                             gas_yield[iterations]

            GWP.append(calculated_GWP)
        return GWP

    # Employ GWP calculation function
    GWP_syngas_combustion = syngas_combustion_CO2_eq(scaled_gas_fractions, gas_yield)  # [kg CO2 per kg feedstock in]

    # Return final calculated GWPs from syngas combustion
    return GWP_syngas_combustion
