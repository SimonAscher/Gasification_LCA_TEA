import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error

from config import settings
from functions.MonteCarloSimulation import get_distribution_draws
from functions.general.utility import get_project_root
from functions.TEA import convert_currency_annual_average
from functions.TEA.scaling import CEPCI_scale
from objects import triangular_dist_maker


def get_CHP_CAPEX_distribution(system_size_kWel, currency=None, CEPCI_year=None):
    """
    Calculate the CAPEX distribution of a CHP plant.

    Parameters
    ----------
    system_size_kWel: float
        Required CHP size/power rating [kWel].
    currency: str
        Currency that is to be used for analysis.
    CEPCI_year: int
        Reference CEPCI year that is to be used for analysis.


    Returns
    -------
    list
        Distribution of CAPEX values in the supplied currency.

    """
    # Get defaults
    if currency is None:
        currency = settings.user_inputs.general.currency

    if CEPCI_year is None:
        CEPCI_year = settings.user_inputs.economic.CEPCI_year

    # Load data
    root_dir = get_project_root()
    data_file = "CAPEX_CHP.csv"
    data_file_path = os.path.join(root_dir, "data", data_file)
    df = pd.read_csv(data_file_path)

    # Convert all values to same currency and update to most recent CEPCI value
    CAPEX_currency_scaled = []
    CAPEX_currency_CEPCI_scaled = []

    for row_no in df.index:
        CAPEX_currency_scaled.append(convert_currency_annual_average(value=df["CAPEX"][row_no],
                                                                     year=df["Reference Year"][row_no],
                                                                     base_currency=df["Currency"][row_no],
                                                                     converted_currency=currency))
        CAPEX_currency_CEPCI_scaled.append(CEPCI_scale(base_year=df["Reference Year"][row_no],
                                                       design_year=CEPCI_year,
                                                       value=CAPEX_currency_scaled[row_no]))

    # Add (i) currency and (ii) currency + CEPCI scaled values to dataframe
    currency_scaled_label = "CAPEX_" + currency
    currency_and_CEPCI_scaled_label = "CAPEX_" + currency + "_CEPCI_" + str(CEPCI_year)
    df[currency_scaled_label] = CAPEX_currency_scaled
    df[currency_and_CEPCI_scaled_label] = CAPEX_currency_CEPCI_scaled

    # Define thresholds to split data set into small scale and medium scale plants
    threshold_small_scale_system = 5000  # kW
    threshold_medium_scale_system = 500000  # kW

    def get_polynomial_model_and_performance(dataframe, display_fit=False):
        """
        Returns polynomial model and its performance.

        Parameters
        ----------
        dataframe
        display_fit

        Returns
        -------

        """
        # Extract x and y data and sort it
        x = dataframe["Plant size [kWel]"]
        y = dataframe[currency_and_CEPCI_scaled_label]
        temp_sorting_df = pd.DataFrame({'x_sorted':x, 'y_sorted':y})
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

            return {"model": poly_reg_model, "R2": model_r2, "RMSE": model_rmse, "predictions": y_predicted, "degree": degree}

        # Check if 1st or 2nd degree polynomial performs better
        first_degree_results = fit_polynomial_regression_and_get_performance(degree=1)
        second_degree_results = fit_polynomial_regression_and_get_performance(degree=2)
        if first_degree_results["RMSE"] < second_degree_results["RMSE"]:
            results = first_degree_results
        else:
            results = second_degree_results

        if display_fit:
            # Plot with fit
            sns.scatterplot(data=dataframe, x="Plant size [kWel]", y=currency_and_CEPCI_scaled_label, hue="Type")
            plt.plot(x, results["predictions"], c="red")
            plt.xlabel("Plant size [kW${_{el}}$]")
            plt.ylabel("CAPEX [GBP]")
            plt.xticks(rotation=45)
            plt.show()

        return results

    # Get predictions
    if system_size_kWel < threshold_small_scale_system:  # small scale
        df_small = df[df["Plant size [kWel]"] < threshold_small_scale_system]
        regression_model_results = get_polynomial_model_and_performance(df_small)
    else:  # medium scale
        if system_size_kWel < threshold_medium_scale_system:
            df_medium = df[(df["Plant size [kWel]"] > threshold_small_scale_system) &
                           (df["Plant size [kWel]"] <= threshold_medium_scale_system)]
            regression_model_results = get_polynomial_model_and_performance(df_medium)
        else:  # too large - not supported
            raise ValueError("CHP size exceeds the supported size.")

    # Make predictions
    prediction = regression_model_results["model"].predict(PolynomialFeatures(
        degree=regression_model_results["degree"], include_bias=False).
                                                           fit_transform(np.array(system_size_kWel).reshape(-1, 1)))
    error = regression_model_results["RMSE"]

    distribution = triangular_dist_maker(lower=prediction-error, mode=prediction, upper=prediction+error)

    distribution_draws = list(get_distribution_draws(distribution))

    return distribution_draws
