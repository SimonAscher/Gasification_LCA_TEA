import toml

from functions.general.utility.path_handling import get_project_root
from objects import fixed_dist_maker, range_dist_maker, triangular_dist_maker, gaussian_dist_maker

# NOTE: THESE FUNCTIONS ARE CURRENTLY NOT USED - default paths to files are incorrect too


def update_user_inputs_toml(variable_name, variable_value, relative_filepath=None):
    """
    Function to add a user input to toml file.

    Parameters
    ----------
    variable_name: str
        Gives the name of the variable which is to be created.
    variable_value:
        Gives the value for the newly created variable.
    relative_filepath
        Relative raw (i.e. string preceded by r) file path to user inputs toml file.
    """
    root_path = get_project_root()
    if relative_filepath is None:
        relative_filepath = str(root_path) + r"configs\user_inputs.toml"
    else:
        relative_filepath = str(root_path) + relative_filepath

    # Load toml
    data = toml.load(relative_filepath)

    # Update value
    data["default"]["user_inputs"][variable_name] = variable_value

    # Update toml
    f = open(relative_filepath, 'w')
    toml.dump(data, f)
    f.close()


def reset_user_inputs_toml(relative_filepath=None):
    """
    Function to reset toml file and clear all variables.

    Parameters
    ----------
    relative_filepath
        Relative raw (i.e. string preceded by r) file path to user inputs toml file.
    """
    root_path = get_project_root()
    if relative_filepath is None:
        relative_filepath = str(root_path) + r"configs\user_inputs.toml"
    else:
        relative_filepath = str(root_path) + relative_filepath

    # Create dictionary to initialise file
    default_data = {'default': {'user_inputs': {}}}

    # Update file
    f = open(relative_filepath, 'w')
    toml.dump(default_data, f)
    f.close()


def user_input_to_dist_maker(user_input):
    """
    Function to turn a distribution maker object saved in a toml file back into a distribution maker object.

    Parameters
    ----------
    user_input: DynaBox
        User input of DynaBox type from settings file.
    Returns
    -------
    None | fixed_dist_maker | range_dist_maker | triangular_dist_maker | gaussian_dist_maker
    """

    if user_input == "None":
        dist_maker_object = None

    elif user_input.dist_type == "fixed_dist_maker":
        dist_maker_object = fixed_dist_maker(value=user_input.dist_values.value)

    elif user_input.dist_type == "range_dist_maker":
        dist_maker_object = range_dist_maker(low=user_input.dist_values.low, high=user_input.dist_values.high)

    elif user_input.dist_type == "triangular_dist_maker":
        dist_maker_object = triangular_dist_maker(lower=user_input.dist_values.lower, mode=user_input.dist_values.mode,
                                                  upper=user_input.dist_values.upper)

    elif user_input.dist_type == "gaussian_dist_maker":
        dist_maker_object = gaussian_dist_maker(mean=user_input.dist_values.mean, std=user_input.dist_values.std)
    else:
        raise ValueError("Wrong distribution type.")

    return dist_maker_object
