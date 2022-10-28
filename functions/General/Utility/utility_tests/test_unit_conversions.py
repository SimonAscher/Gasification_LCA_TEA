import pytest
from pytest import approx
from functions.general.utility import kJ_to_kWh, MJ_to_kWh

def test_kJ_to_kWh():
    assert kJ_to_kWh(3600) == approx(1)
    assert kJ_to_kWh(1, reverse=True) == approx(3600)

def test_MJ_to_kWh():
    # Check that output array is correct length - i.e. as required by ML models
    assert MJ_to_kWh(3600) == approx(1000)
    assert MJ_to_kWh(1000, reverse=True) == approx(3600)
