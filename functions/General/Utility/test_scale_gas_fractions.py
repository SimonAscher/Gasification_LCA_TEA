import numpy as np
import pytest

from functions.general.utility._scale_gas_fractions import scale_gas_fractions


# Test np.array part of function
@pytest.mark.parametrize("inp,exp,fmt", [
    ([20, 10, 30, 20, 5, 8], 1, "decimals"),
    ([0.20, 0.10, 0.30, 0.20, 0.05, 0.08], 1, "percentages")
])
def test_scale_gas_fractions_np_array(inp, exp, fmt):
    assert sum(scale_gas_fractions(np.array(inp), gas_fractions_format=fmt)) == pytest.approx(exp)


# Test dictionary part of function
test_dict_input = {'N2 [vol.% db]': [40.74566724250848, 52.843272458780184],
                   'H2 [vol.% db]': [8.855640458702718, 11.648281545514177],
                   'CO [vol.% db]': [12.188864834712685, 14.275455216524598],
                   'CO2 [vol.% db]': [16.612180962024706, 16.01085603137923],
                   'CH4 [vol.% db]': [3.037460311092858, 3.2344031516060077],
                   'C2Hn [vol.% db]': [1.9747516026113656, 1.449719081651092]
                   }


def test_scale_gas_fractions_dict():
    output = scale_gas_fractions(test_dict_input, gas_fractions_format="percentages")

    # Check if all outputs sum up to 1
    sums = []
    for iteration in np.arange(len(output[list(output.keys())[0]])):
        values = []
        for key in output.keys():
            values.append(output[key][iteration])
        total = sum(values)
        sums.append(total)

    assert sums == pytest.approx([1, 1])

# Check that errors work properly
@pytest.mark.parametrize("inp", [dict(a=1)])
def test_scale_gas_fractions_fails(inp):
    with pytest.raises(ValueError):
        scale_gas_fractions(inp)
