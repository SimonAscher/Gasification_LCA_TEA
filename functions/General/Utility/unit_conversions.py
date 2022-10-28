# Simple tested functions to convert between different units

# Energy units

def kJ_to_kWh(value, reverse=False):
    value_out = value / 3600
    if reverse:
        value_out = 3600 * value

    return value_out


def MJ_to_kWh(value, reverse=False):
    value_out = value / 3.6
    if reverse:
        value_out = 3.6 * value

    return value_out
