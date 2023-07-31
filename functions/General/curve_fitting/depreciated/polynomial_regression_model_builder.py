import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pandas import DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error


def get_polynomial_model_and_performance(dataframe, x_data_label, y_data_label, degree=None, plot_x_label=None, plot_y_label=None,
                                         plot_hue_label=None, display_fit=False):
    """
    DEPRECIATED - use display_curve_fits instead

    Returns polynomial model and its performance. Used for CAPEX estimation.

    Parameters
    ----------
    dataframe: DataFrame
        Pandas dataframe containing the data used for modelling.
    x_data_label: str
        Indicates the column name with the x_source data.
    y_data_label: str
        Indicates the column name with the y_source data.
    degree: None | int
        Degree of polynomial - if None one automatically gets selected purely based on the RMSE of the fit.
        Note: This may lead to errors.
    plot_x_label: None | str
        x_source label for plots. Only required if display_fit=True.
    plot_y_label: None | str
        y_source label for plots. Only required if display_fit=True.
    plot_hue_label: None | str
        Determines which column should be used as hue property in seaborn plots.
    display_fit: bool
        Determines whether plot is to be shown or not.

    Returns
    -------

    """
    # Extract x_source and y_source data and sort it
    x = dataframe[x_data_label]
    y = dataframe[y_data_label]
    temp_sorting_df = pd.DataFrame({'x_sorted': x, 'y_sorted': y})
    temp_sorting_df = temp_sorting_df.sort_values('x_sorted')
    x = np.array(temp_sorting_df["x_sorted"])
    y = np.array(temp_sorting_df["y_sorted"])

    def fit_polynomial_regression_and_get_performance(degree):
        """
        Fits nth degree polynomial and returns regression models and its performance.

        Parameters
        ----------
        degree: int

        Returns
        -------

        """
        # Get polynomial features and fit regression model
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        poly_features = poly.fit_transform(x.reshape(-1, 1))
        poly_reg_model = LinearRegression()
        poly_reg_model.fit(poly_features, y)
        y_predicted = poly_reg_model.predict(poly_features)

        # Get error scores
        model_r2 = r2_score(y, y_predicted)
        model_rmse = mean_squared_error(y, y_predicted, squared=False)

        return {"model": poly_reg_model, "R2": model_r2, "RMSE": model_rmse, "predictions": y_predicted,
                "degree": degree}

    if degree is None:

        # Check if 1st or 2nd degree polynomial performs better
        first_degree_results = fit_polynomial_regression_and_get_performance(degree=1)
        second_degree_results = fit_polynomial_regression_and_get_performance(degree=2)
        third_degree_results = fit_polynomial_regression_and_get_performance(degree=3)

        if first_degree_results["RMSE"] < second_degree_results["RMSE"] and \
                first_degree_results["RMSE"] < third_degree_results["RMSE"]:
            results = first_degree_results
        else:
            if second_degree_results["RMSE"] < third_degree_results["RMSE"]:
                results = second_degree_results
            else:
                results = third_degree_results
    else:
        results = fit_polynomial_regression_and_get_performance(degree=degree)

    if display_fit:
        # Get smoothed data points for plotting
        x_smooth = np.linspace(start=x.min(), stop=1.5*x.max(), num=500)
        poly = PolynomialFeatures(degree=results["degree"], include_bias=False)
        poly.fit_transform(x_smooth.reshape(-1, 1))
        y_predicted_smooth = results["model"].predict(poly.fit_transform(x_smooth.reshape(-1, 1)))

        # Plot with fit
        sns.scatterplot(data=dataframe, x=x_data_label, y=y_data_label, hue=plot_hue_label)
        plt.plot(x_smooth, y_predicted_smooth, c="red")
        plt.plot(x, results["predictions"], c="green")
        plt.xlabel(plot_x_label)
        plt.ylabel(plot_y_label)
        plt.xticks(rotation=45)
        plt.show()

    return results
