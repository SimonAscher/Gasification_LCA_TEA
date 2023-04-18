import pytest
from pytest import approx

# from functions.LCA.energy_use import thermal_energy_GWP, electricity_GWP

# Unused currently due to circular import error
# TODO: Fix this test
# def test_thermal_energy_GWP():
#     assert thermal_energy_GWP(1000) == approx(222)
#     assert thermal_energy_GWP(1000, units='kJ') == approx(222 / 3600)
#     assert thermal_energy_GWP(1000, units='MJ') == approx(222 / 3.6)
#
# def test_electricity_GWP():
#     assert electricity_GWP(amount=1000, country="UK") == approx(0.21233 * 1000)
