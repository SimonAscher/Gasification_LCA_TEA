import pytest

from pytest import approx

from processes.syngas_combustion.utils import get_conversion_ratios_to_CO2


# Check that stored molar mass data is correct
def test_get_correct_conversions():
    output = get_conversion_ratios_to_CO2()

    assert output["CO"] == approx((2*44)/(2*28))  # 2 CO + O2 -> 2 CO2
    assert output["CH4"] == approx(44/16)  # CH4 + 2O2 -> CO2 + 2 H2O
    assert output["C2H4"] == approx((2*44)/28)  # C2H4 + 3 O2 -> 2 CO2 + 2 H2O
