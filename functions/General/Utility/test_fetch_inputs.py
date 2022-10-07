import pytest
from functions.general.utility import fetch_ML_inputs

def test_fetch_inputs_function():
    assert len(fetch_ML_inputs()) == 24
