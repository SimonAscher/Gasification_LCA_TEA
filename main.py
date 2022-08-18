# Import the settings settings from config.py
from config import settings

print(settings.general.iterations_MC)
print(settings.general.country)
print(settings.general.CO2_equivalents.electricity.UK)
print(settings.general.CO2_equivalents.electricity)

import get_CO2_equ.py

print(get_CO2_equ())
