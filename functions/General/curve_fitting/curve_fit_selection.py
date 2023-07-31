import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from sklearn.metrics import r2_score, mean_squared_error

from functions.general import MAPE
from functions.general.curve_fitting import func_straight_line, func_power_curve, func_exponential, \
    func_2nd_degree_polynomial, func_3rd_degree_polynomial


def display_curve_fits(dataframe, x_data_label, y_data_label, plot_x_label=None, plot_y_label=None,
                       plot_custom_x_range=None, display_results=True):
    """
    Display various curve fits to a data set given as a pandas dataframe. x and y data given by specifying column
    labels.

    Parameters
    ----------
    dataframe
    x_data_label
    y_data_label
    plot_x_label
    plot_y_label
    plot_custom_x_range: None | list[float, float]
        List of form [Start, End].
    display_results

    Returns
    -------
    dict
        Dictioniary of optimised constants for fitted curves, error metrics, and x range.
    """

    # Get defaults
    if plot_x_label is None:
        plot_x_label = x_data_label
    if plot_y_label is None:
        plot_y_label = y_data_label

    x_source = np.array(dataframe[x_data_label])
    y_source = np.array(dataframe[y_data_label])

    # Create x arrays across various ranges
    x_data_range = np.linspace(start=min(x_source), stop=max(x_source), num=100)
    x_data_range_x5 = np.linspace(start=min(x_source), stop=max(x_source) * 5, num=100)
    if plot_custom_x_range is not None:
        x_user_defined_range = np.linspace(start=min(plot_custom_x_range), stop=max(plot_custom_x_range), num=100)

    # Fit curves
    # Straight line fit
    optimised_constants_straight_line, _ = curve_fit(func_straight_line, x_source, y_source)
    y_fit_straight_line_data_range = func_straight_line(x_data_range, *optimised_constants_straight_line)
    y_fit_straight_line_data_range_x5 = func_straight_line(x_data_range_x5, *optimised_constants_straight_line)
    if plot_custom_x_range is not None:
        y_fit_straight_line_user_defined_data_range = func_straight_line(x_user_defined_range,
                                                                         *optimised_constants_straight_line)
    # Power curve fit
    optimised_constants_power_curve, _ = curve_fit(func_power_curve, x_source, y_source, maxfev=10000)
    y_fit_power_curve_data_range = func_power_curve(x_data_range, *optimised_constants_power_curve)
    y_fit_power_curve_data_range_x5 = func_power_curve(x_data_range_x5, *optimised_constants_power_curve)
    if plot_custom_x_range is not None:
        y_fit_power_curve_user_defined_data_range = func_power_curve(x_user_defined_range,
                                                                     *optimised_constants_power_curve)

    # 2nd degree polynomial fit
    optimised_constants_2nd_degree_polynomial, _ = curve_fit(func_2nd_degree_polynomial, x_source, y_source)
    y_fit_2nd_degree_polynomial_data_range = func_2nd_degree_polynomial(x_data_range,
                                                                        *optimised_constants_2nd_degree_polynomial)
    y_fit_2nd_degree_polynomial_data_range_x5 = func_2nd_degree_polynomial(x_data_range_x5,
                                                                           *optimised_constants_2nd_degree_polynomial)
    if plot_custom_x_range is not None:
        y_fit_2nd_degree_polynomial_user_defined_data_range = func_2nd_degree_polynomial(x_user_defined_range,
                                                                                         *optimised_constants_2nd_degree_polynomial)

    # 3rd degree polynomial fit
    optimised_constants_3rd_degree_polynomial, _ = curve_fit(func_3rd_degree_polynomial, x_source, y_source)
    y_fit_3rd_degree_polynomial_data_range = func_3rd_degree_polynomial(x_data_range,
                                                                        *optimised_constants_3rd_degree_polynomial)
    y_fit_3rd_degree_polynomial_data_range_x5 = func_3rd_degree_polynomial(x_data_range_x5,
                                                                           *optimised_constants_3rd_degree_polynomial)
    if plot_custom_x_range is not None:
        y_fit_3rd_degree_polynomial_user_defined_data_range = func_3rd_degree_polynomial(x_user_defined_range,
                                                                                         *optimised_constants_3rd_degree_polynomial)

    # # Exponential fit
    # optimised_constants_exp_curve, _ = curve_fit(func_exponential, x_source, y_source, method="dogbox", maxfev=1000)
    # y_fit_exp_curve_data_range = func_exponential(x_data_range, *optimised_constants_exp_curve)
    # y_fit_exp_curve_data_range_x5 = func_exponential(x_data_range_x5, *optimised_constants_exp_curve)
    # if plot_custom_x_range is not None:
    #     y_fit_exp_curve_user_defined_data_range = func_exponential(x_user_defined_range, *optimised_constants_exp_curve)

    # Get R2 and RMSE scores
    # Straight line fit
    r2_straight_line = r2_score(y_source, func_straight_line(x_source, *optimised_constants_straight_line))
    rmse_straight_line = mean_squared_error(y_source,
                                            func_straight_line(x_source, *optimised_constants_straight_line),
                                            squared=False)
    mape_straight_line = MAPE(y_source, func_straight_line(x_source, *optimised_constants_straight_line))

    # Power curve fit
    r2_power_curve = r2_score(y_source, func_power_curve(x_source, *optimised_constants_power_curve))
    rmse_power_curve = mean_squared_error(y_source,
                                          func_power_curve(x_source, *optimised_constants_power_curve),
                                          squared=False)
    mape_power_curve = MAPE(y_source, func_power_curve(x_source, *optimised_constants_power_curve))

    # 2nd degree polynomial fit
    r2_2nd_degree_polynomial = r2_score(y_source, func_2nd_degree_polynomial(x_source,
                                                                             *optimised_constants_2nd_degree_polynomial))
    rmse_2nd_degree_polynomial = mean_squared_error(y_source,
                                                    func_2nd_degree_polynomial(x_source,
                                                                               *optimised_constants_2nd_degree_polynomial),
                                                    squared=False)
    mape_2nd_degree_polynomial = MAPE(y_source, func_2nd_degree_polynomial(x_source,
                                                                           *optimised_constants_2nd_degree_polynomial))
    # 3rd degree polynomial fit
    r2_3rd_degree_polynomial = r2_score(y_source, func_3rd_degree_polynomial(x_source,
                                                                             *optimised_constants_3rd_degree_polynomial))
    rmse_3rd_degree_polynomial = mean_squared_error(y_source,
                                                    func_3rd_degree_polynomial(x_source,
                                                                               *optimised_constants_3rd_degree_polynomial),
                                                    squared=False)
    mape_3rd_degree_polynomial = MAPE(y_source, func_3rd_degree_polynomial(x_source,
                                                                           *optimised_constants_3rd_degree_polynomial))

    # r2_exponential_curve = r2_score(y_source, func_exponential(x_source, *optimised_constants_exp_curve))
    # rmse_exponential_curve = mean_squared_error(y_source,
    #                                             func_exponential(x_source, *optimised_constants_exp_curve),
    #                                             squared=False)

    if display_results:
        # Display error scores
        print(f"Straight line fit: R2: {r2_straight_line:.3f}; RMSE: {rmse_straight_line:.0f}; MAPE: {mape_straight_line:.0f} %")
        print(f"Power curve fit: R2: {r2_power_curve:.3f}; RMSE: {rmse_power_curve:.0f}; MAPE: {mape_power_curve:.0f} %")
        print(f"2nd degree polynomial fit: R2: {r2_2nd_degree_polynomial:.3f}; RMSE: {rmse_2nd_degree_polynomial:.0f}; MAPE: {mape_2nd_degree_polynomial:.0f} %")
        print(f"3rd degree polynomial: R2: {r2_3rd_degree_polynomial:.3f}; RMSE: {rmse_3rd_degree_polynomial:.0f}; MAPE: {mape_3rd_degree_polynomial:.0f} %")
        # print(f"Exponential fit: R2: {r2_exponential_curve:.3f}; RMSE: {rmse_exponential_curve:.0f}")

        # # Create labels if desired
        # straight_line_label = f"y = {optimised_constants_straight_line[0]}x + {optimised_constants_straight_line[1]}"

        # Create plot across initial data range
        fig, ax = plt.subplots(dpi=150)
        ax.scatter(x_source, y_source, color="black", label="Data", zorder=10)
        ax.plot(x_data_range, y_fit_straight_line_data_range, '--', color='red', label="straight line")
        ax.plot(x_data_range, y_fit_power_curve_data_range, '--', color='blue', label="power curve")
        ax.plot(x_data_range, y_fit_2nd_degree_polynomial_data_range, '--', color='green', label="2nd degree polynomial")
        ax.plot(x_data_range, y_fit_3rd_degree_polynomial_data_range, '--', color='purple', label="3rd degree polynomial")
        # ax.plot(x_data_range, y_fit_exp_curve_data_range, '--', color='orange', label="exponential curve")
        ax.set_xlabel(plot_x_label)
        ax.set_ylabel(plot_y_label)
        plt.legend()
        plt.show()

        # Create plot across x5 data range
        fig, ax = plt.subplots(dpi=150)
        ax.scatter(x_source, y_source, color="black", label="Data", zorder=10)
        ax.plot(x_data_range_x5, y_fit_straight_line_data_range_x5, '--', color='red', label="straight line")
        ax.plot(x_data_range_x5, y_fit_power_curve_data_range_x5, '--', color='blue', label="power curve")
        ax.plot(x_data_range_x5, y_fit_2nd_degree_polynomial_data_range_x5, '--', color='green',
                label="2nd degree polynomial")
        ax.plot(x_data_range_x5, y_fit_3rd_degree_polynomial_data_range_x5, '--', color='purple',
                label="3rd degree polynomial")
        # ax.plot(x_data_range_x5, y_fit_exp_curve_data_range_x5, '--', color='orange', label="exponential curve")
        ax.set_xlabel(plot_x_label)
        ax.set_ylabel(plot_y_label)
        plt.legend()
        plt.show()

        if plot_custom_x_range is not None:
            # Create plot across user defined range
            fig, ax = plt.subplots(dpi=150)
            ax.scatter(x_source, y_source, color="black", label="Data", zorder=10)
            ax.plot(x_user_defined_range, y_fit_straight_line_user_defined_data_range, '--', color='red',
                    label="straight line")
            ax.plot(x_user_defined_range, y_fit_power_curve_user_defined_data_range, '--', color='blue',
                    label="power curve")
            ax.plot(x_user_defined_range, y_fit_2nd_degree_polynomial_user_defined_data_range, '--', color='green',
                    label="2nd degree polynomial")
            ax.plot(x_user_defined_range, y_fit_3rd_degree_polynomial_user_defined_data_range, '--', color='purple',
                    label="3rd degree polynomial")
            # ax.plot(x_user_defined_range, y_fit_exp_curve_user_defined_data_range, '--', color='orange',
            #         label="exponential curve")
            ax.set_xlabel(plot_x_label)
            ax.set_ylabel(plot_y_label)
            plt.legend()
            plt.show()

    summary = {"straight_line": {"Constants": optimised_constants_straight_line,
                                "R2": r2_straight_line,
                                "RMSE": rmse_straight_line},
              "power_curve": {"Constants": optimised_constants_power_curve,
                              "R2": r2_power_curve,
                              "RMSE": rmse_power_curve},
              # "exponential_curve": {"Constants": optimised_constants_exp_curve,
              #                       "R2": r2_exponential_curve,
              #                       "RMSE": rmse_exponential_curve},
              "2nd_degree_polynomial": {"Constants": optimised_constants_2nd_degree_polynomial,
                                        "R2": r2_2nd_degree_polynomial,
                                        "RMSE": rmse_2nd_degree_polynomial},
              "3rd_degree_polynomial": {"Constants": optimised_constants_3rd_degree_polynomial,
                                        "R2": r2_3rd_degree_polynomial,
                                        "RMSE": rmse_3rd_degree_polynomial},
               "data_range": {"min": min(x_source),
                              "max": max(x_source)}
               }

    return summary
