import pytest

from processes.syngas_combustion.utils import get_molar_masses


# Check that stored molar mass data is correct
def test_get_molar_masses():
    output = get_molar_masses()
    assert output.N2 == 28
    assert output.H2 == 2
    assert output.CO == 28
    assert output.CO2 == 44
    assert output.CH4 == 16
    assert output.C2H4 == 28
    assert output.O == 16
    assert output.H2O == 18
