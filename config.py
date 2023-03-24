# Import Dynaconf
from dynaconf import Dynaconf

# Create settings instance
settings = Dynaconf(
    settings_files=[  # Paths to toml files
        "configs/default_settings.toml",  # a file for default settings
        "configs/user_inputs_default.toml",  # default user inputs
        # "configs/user_inputs.toml",  # overwrite default user inputs
        "configs/.secrets.toml"  # a file for sensitive data (gitignored)
    ],

    environments=True,  # Enable layered environments
)

# %% Set up validators and defaults
# settings.validators.register(
#     # add validators here
#     # More details on https://www.dynaconf.com/validation/
# )
# settings.validators.validate()
