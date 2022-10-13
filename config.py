# Import Dynaconf
from dynaconf import Dynaconf  # , Validator

# Create settings instance
settings = Dynaconf(
    settings_files=[  # Paths to toml files
        "configs/default_settings.toml",  # a file for default settings
        # "configs/generic_user_inputs.toml",  # generic user inputs
        "configs/user_inputs.toml",  # a file for user inputs
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
