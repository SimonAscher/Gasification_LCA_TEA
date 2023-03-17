import pytest

from functions.TEA import get_present_value

def test_get_pv_av_case():
    assert get_present_value(value=1234, value_type="AV") == pytest.approx(15378.37)

def test_get_pv_fv_case():
    assert get_present_value(value=5678, value_type="FV") == pytest.approx(2139.98)

def test_get_pv_other_str_case():
    with pytest.raises(ValueError):
        get_present_value(value=3000, value_type="Wrong String")
