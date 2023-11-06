# Import Dynaconf
from dynaconf import Dynaconf

from pathlib import Path

# Get root path
root_path = str(Path(__file__).parent)

# Create settings instance
settings = Dynaconf(
    settings_files=[  # Paths to toml files
        root_path + r"\configs\default_settings.toml",  # a file for default settings
        root_path + r"\configs\user_inputs_defaults.toml",  # default user inputs
        # root_path + r"\configs\user_inputs\predefined\user_inputs_Gai_IntJHydrog_2012_37.toml",  # user inputs (overwrites defaults)
        # root_path + r"\configs\user_inputs\predefined\user_inputs_Wang_IntJHydrog_2012_37.toml",  # user inputs (overwrites defaults)
        # root_path + r"\configs\user_inputs\predefined\user_inputs_Song_BiomassBioenergy_2012_36.toml",  # user inputs (overwrites defaults)
        root_path + r"\configs\user_inputs\predefined\user_inputs_Ascher_Energy_2019_181.toml",
        # user inputs (overwrites defaults)
        root_path + r"\configs\sensitivity_analysis_defaults.toml",  # default sensitivity analysis choices
        root_path + r"\configs\secrets.toml"  # a file for sensitive data (gitignored)
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
