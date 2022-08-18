# Import Dynaconf
from dynaconf import Dynaconf  # , Validator

# Create settings instance
settings = Dynaconf(
    settings_files=[  # Paths to toml files
        "configs/default_settings.toml",  # a file for default settings
        "configs/settings.toml",  # a file for main settings
        "configs/.secrets.toml"  # a file for sensitive data (gitignored)
    ],

    environments=True,  # Enable layered environments
    # dotenv_path="configs/.env"  # custom path for .env file to be loaded
)

# %% Set up validators and defaults
# settings.validators.register(
#     # add validators here
#     # More details on https://www.dynaconf.com/validation/
# )
# settings.validators.validate()
