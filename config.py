# Import Dynaconf
from dynaconf import Dynaconf

# Create settings instance
settings = Dynaconf(
    settings_files=[  # Paths to toml files
        "configs/default_settings.toml",  # a file for default settings
        "configs/user_inputs_defaults.toml",  # default user inputs
        "configs/user_inputs/user_inputs_Gai_IntJHydrog_2012_37.toml",  # user inputs (overwrites defaults)
        "configs/secrets.toml"  # a file for sensitive data (gitignored)
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
