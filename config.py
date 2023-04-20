# Import Dynaconf
from dynaconf import Dynaconf

from pathlib import Path

# Get root path
root_path = Path(__file__).parent

# Create settings instance
settings = Dynaconf(
    settings_files=[  # Paths to toml files
        str(root_path) + r"\configs\default_settings.toml",  # a file for default settings
        str(root_path) + r"\configs\user_inputs_defaults.toml",  # default user inputs
        str(root_path) + r"\configs\user_inputs\user_inputs_Gai_IntJHydrog_2012_37.toml",  # user inputs (overwrites defaults)
        str(root_path) + r"\configs\secrets.toml"  # a file for sensitive data (gitignored)
    ],
    environments=True,  # Enable layered environments
    merge_enabled=True  # Allows for default inputs to be overwritten
)

# %% Set up validators and defaults
# settings.validators.register(
#     # add validators here
#     # More details on https://www.dynaconf.com/validation/
# )
# settings.validators.validate()
