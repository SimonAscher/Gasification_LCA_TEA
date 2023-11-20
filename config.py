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
        # root_path + r"\configs\user_inputs\predefined\user_inputs_Gai_2012_IntJHydrog_37.toml",  # user inputs (overwrites defaults)
        # root_path + r"\configs\user_inputs\predefined\user_inputs_Wang_2012_IntJHydrog_37.toml",  # user inputs (overwrites defaults)
        # root_path + r"\configs\user_inputs\predefined\user_inputs_Song_2012_BiomassBioenergy_36.toml",  # user inputs (overwrites defaults)
        # root_path + r"\configs\user_inputs\predefined\user_inputs_Ascher_2019_Energy_181.toml",  # user inputs (overwrites defaults)
        # root_path + r"\configs\user_inputs\predefined\user_inputs_Salkuyeh_2018_IntJHyrdog_43.toml",  # user inputs (overwrites defaults)
        # root_path + r"\configs\user_inputs\predefined\user_inputs_Parascanu_2019_Energy_189.toml", # user inputs (overwrites defaults)
        # root_path + r"\configs\user_inputs\predefined\user_inputs_Dong_2018_SciTotalEnviron_626.toml", # user inputs (overwrites defaults)
        # root_path + r"\configs\user_inputs\predefined\user_inputs_Zang_2018_IntJGreenhGasControl_78_CCS.toml",  # user inputs (overwrites defaults)
        root_path + r"\configs\user_inputs\predefined\user_inputs_Puy_2010_BiomassBioenergy_34.toml",  # user inputs (overwrites defaults)
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
