def func_straight_line(x, a, b):
    return a * x + b


def func_power_curve(x, a, b, c):
    return a * x ** b + c


def func_2nd_degree_polynomial(x, a, b, c):
    return a * x + b * x ** 2 + c


def func_3rd_degree_polynomial(x, a, b, c, d):
    return (a * x) + (b * x ** 2) + (c * x ** 3) + d


def func_exponential(x, a, b, c):
    return a * np.exp(-b * x) + c