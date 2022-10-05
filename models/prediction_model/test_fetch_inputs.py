import pytest
from models.prediction_model import fetch_inputs

def test_fetch_inputs_function():
    assert len(fetch_inputs()) == 24
