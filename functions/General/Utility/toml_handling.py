import toml


def update_user_inputs_toml(variable_name, variable_value,
                            absolute_raw_filepath=r"C:\Users\2270577A\PycharmProjects"
                                                  r"\PhD_LCA_TEA\configs\user_inputs.toml"):
    """
    Function to add a user input to toml file.

    Parameters
    ----------
    variable_name: str
        Gives the name of the variable which is to be created.
    variable_value:
        Gives the value for the newly created variable.
    absolute_raw_filepath
        Absolute raw (i.e. string preceded by r) file path to user inputs toml file.
    """

    # Load toml
    data = toml.load(absolute_raw_filepath)

    # Update value
    data["default"]["user_inputs"][variable_name] = variable_value

    # Update toml
    f = open(absolute_raw_filepath, 'w')
    toml.dump(data, f)
    f.close()

    #TODO: Optional - could extend this to work for any toml file and for any structure
    # let function select how deep the to be updated variable is
    # i.e. ["general"]["user_inputs"]["variable_to_be_updated"] (or however many brackets are required)


def reset_user_inputs_toml(absolute_raw_filepath=r"C:\Users\2270577A\PycharmProjects"
                                                 r"\PhD_LCA_TEA\configs\user_inputs.toml"):
    """
    Function to reset toml file and clear all variables.

    Parameters
    ----------
    absolute_raw_filepath
        Absolute raw (i.e. string preceded by r) file path to user inputs toml file.
    """

    # Create dictionary to initialise file
    default_data = {'default': {'user_inputs': {}}}

    # Update file
    f = open(absolute_raw_filepath, 'w')
    toml.dump(default_data, f)
    f.close()