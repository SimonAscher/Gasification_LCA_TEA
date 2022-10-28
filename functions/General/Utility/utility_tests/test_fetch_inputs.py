import pytest
from functions.general.utility import fetch_ML_inputs

def test_fetch_inputs_function():
    # Check that output array is correct length - i.e. as required by ML models
    assert len(fetch_ML_inputs()) == 24
