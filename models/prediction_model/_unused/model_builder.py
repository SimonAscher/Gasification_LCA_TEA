# %% Import required packages
# %% Import required libraries

# Import basic operations and plotting
import pandas as pd

import numpy as np
# import math
import pickle
import seaborn as sns
# import matplotlib
import matplotlib.pyplot as plt
# import scipy.stats as stats

# Import filters to remove unnecessary warnings
from warnings import simplefilter
from sklearn.exceptions import ConvergenceWarning

# Import error performance measure, preprocessing etc. from sklearn
from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV, RandomizedSearchCV, RepeatedKFold, ParameterGrid
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score
from sklearn.impute import KNNImputer
# from sklearn.utils.fixes import loguniform
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, MinMaxScaler

from sklearn.pipeline import make_pipeline

# Import Machine Learning Models from sklearn and other libraries
# from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn import svm
from xgboost import XGBRegressor
# import mlens
# from mlens.ensemble import SuperLearner

# Import feature importance assessment methods
from sklearn.inspection import permutation_importance
# import shap

# %% Define prerequisite functions used within model builder function:

# Define additional error measurements:

def MAPE(Y_actual, Y_Predicted):
    # Function to calculate mean absolute percentage error
    error_values = np.abs((Y_actual - Y_Predicted) / Y_actual) * 100
    error_values = np.asarray(error_values)
    inf_mask = ~np.isfinite(error_values)  # check for values which are infinity due to division by zero
    # error_values[inf_mask == True] = 0 # can be used to avoid infinite values - however this is not really a valid assumption - as it would just assume perfect prediction accuracy for all the cases where the true value is zero
    mape = np.mean(error_values)

    return mape  # in percent


def noise_var(Y_actual, Y_Predicted, samples, regressors):
    # Function to calculate the noise variance
    # Need to double check if this is the correct equation etc - currentlyt taken from: : https://towardsdatascience.com/what-to-do-when-your-model-has-a-non-normal-error-distribution-f7c3862e475f

    # noise variance is defined by: s^2 = RSS/(n-p)
    # question - which n should I use. Size of test set, size of entire data set? - do not use until that has been resolved
    RSS = np.sum((Y_actual - Y_Predicted) ** 2)
    n = samples
    p = regressors
    noise_variance = (RSS / (n - p))
    return RSS  # note this corresponds to sigma squared not sigma (i.e.variance not standard deviation)


# Other functions:

def check_missing(data):
    # Function to check data for missing values
    no_missing = pd.DataFrame(data).isnull().sum().sum()  # calculate number of missing values in data
    return no_missing


# %% Create one function which can fit any of the considered models with an range of possible pretreatment options
def build_models(X, Y, predictor_pretreatment, target_pretreatment, modelname='RF', random_state=42, CV_folds=5,
                 optimisation=False, iterations_RandSearch='auto', display=True):
    """
    Function to train and test 'N' models for 'N' output/target variables (i.e. one model is trained for each
        ouput variable).
    A number of different ML algorithms are supported and may be defined by the variable 'modelname'.

    Inputs:
    X - predictor data for model training and testing
    Y - target data for model training and testing(multiple target columns possible)
    predictor_pretreatment - specifies the predictor variable pretreatment option
    target_pretreatment - specifies the target variable pretreatment option
    modelname - defines model type (default: 'RF')
    random_state - defines random seed (default: 42)
    CV_folds - define number of cross validation folds (default: 5)
    optimisation - specifies whether hyperparameter tuning is desired or default values are to be used (default: False)
    iterations_RandSearch - specifies the number of iterations for randomised grid search. Higher values cover more combinations but take longer to compute. Should
        be set to a higher value if number of combinations in optimisation grid is high (default: 100)
    display = If True graphs and description of model training are shown. If False these won't be shown (default: True)
    Output:
    performance_summary - pandas dataframe containing trained models, performance measures, and more
    """

    # ---------------------------------------
    # 2.) Select which ML model is to be used and define grid/randomised search parameter grids for hyperparameter optimisation:
    # ---------------------------------------

    if modelname == 'RF':  # Use sklearn's random forest regressor
        model = RandomForestRegressor(random_state=random_state)

        # Define grid/randomised search parameters
        max_depth = max_depth = [int(x) for x in np.linspace(10, 100, num=10)]
        max_depth.append(None)

        param_grid = {
            'n_estimators': [10, 50, 100, 200, 500, 1000, 2000],
            'max_features': ['auto', 'sqrt'],
            'max_depth': max_depth,
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
        }

    elif modelname == 'GBR':  # Use sklearn's gradient boosting regressor
        model = GradientBoostingRegressor(random_state=random_state)

        # Define grid/randomised search parameters
        param_grid = {
            'loss': ['squared_error', 'absolute_error', 'huber'],
            'learning_rate': [0.02, 0.05, 0.10, 0.15, 0.20, 0.50],
            'n_estimators': [10, 50, 100, 200, 500, 1000, 2000],
            'subsample': [0.6, 0.8, 1.0],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_depth': [2, 3, 5, 10],
            'max_features': ['auto', 'sqrt', 0.3],
        }
    elif modelname == 'XGBoost':  # Use xgboost's extreme gradient boosting regressor
        model = XGBRegressor(random_state=random_state)

        param_grid = {
            'n_estimators': [10, 50, 100, 200, 500, 1000, 2000],
            'max_depth': [2, 5, 7, 10],
            'eta': [0.01, 0.1, 0.3],
            'subsample': [0.5, 0.7, 1],
            'colsample_bytree': [0.5, 0.7, 1],
        }

        simplefilter('ignore',
                     category=FutureWarning)  # turn depreciation warnings off - required for versions of XGBoost ealier than 1.6


    elif modelname == 'AdaBoost':  # Use sklearn's AdaBoost regressor
        model = AdaBoostRegressor(random_state=random_state)

        # Define grid/randomised search parameters
        base_estimator_depths = list()  # define depth of decision tree stumps and base model
        for i in range(1, 10, 2):
            base_estimator_depths.insert(i, DecisionTreeRegressor(max_depth=i))

        param_grid = {
            'base_estimator': base_estimator_depths,
            'n_estimators': [10, 50, 100, 200, 500, 1000, 2000],
            'learning_rate': [0.2, 0.5, 1, 1.5, 2, 5],
            'loss': ['linear', 'square', 'exponential']
        }

    elif modelname == 'SVM':  # Use sklearn's support vector machine
        model = make_pipeline(StandardScaler(), svm.SVR())

        if optimisation == True:
            print('Note: Optimisation currently not supported for SVM - change to "False" \n')


    elif modelname == 'ANN':  # Use sklearn's multi-layer perceptron
        model = make_pipeline(StandardScaler(),
                              MLPRegressor(solver='lbfgs', random_state=random_state, early_stopping=True,
                                           max_iter=1000))

        param_grid = {
            'mlpregressor__hidden_layer_sizes': [int(x) for x in np.linspace(3, 15, num=7)],
            'mlpregressor__activation': ['logistic', 'tanh', 'relu'],
            'mlpregressor__solver': ['lbfgs', 'adam'],
            'mlpregressor__early_stopping': [True, False],
            'mlpregressor__max_iter': [200, 500, 1000, 2000]
        }

        simplefilter('ignore', category=ConvergenceWarning)  # turn convergence warnings off


    else:
        print('Error: Model name not defined!')

    if display == True:
        print(modelname, 'model selected!\n')  # show which model has been selected
        print(
            '# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # \n')  # to seperate model selection info from performance information

    if optimisation == True:
        parameter_combinations = len(ParameterGrid(param_grid))
        print('Total number of combinations in optimisation grid:', parameter_combinations,
              '\n')  # show number of combinations in optimisation grid

        if iterations_RandSearch == 'auto':  # Define number of iterations if 'auto' has been selected and no manual numerical input
            iterations_RandSearch = int(
                parameter_combinations * 0.25)  # consider 25% of all possible parameter combinations in optimisation or at least 100
            if iterations_RandSearch < 100:  # set minimum number of iterations to 100
                iterations_RandSearch = 100

            if iterations_RandSearch > 1000:  # set maximum number of iterations to 1000
                iterations_RandSearch = 1000
                print('Random Search Iterations have been limited to 1000 \n')

        print(iterations_RandSearch, 'combinations will be considered in search \n')

        if (
                iterations_RandSearch / parameter_combinations) < 0.10:  # give warning if iterations_RandSearch was manually entered and is low
            print(
                'Warning: Only {:0.2f}% of grid combinations considered in Optimisation. Increase "iterations_RandSearch" or decrease parameter combinations in parameter grid \n'.format(
                    (iterations_RandSearch / parameter_combinations) * 100))

        print(
            '# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # \n')  # to optimisation information from rest of model

    # ------------------------------------------
    # 2.5.) Split data into train and test sets:
    # ------------------------------------------

    test_fraction = 0.15  # define fraction used for testing
    x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=test_fraction, random_state=random_state)

    # ----------------------------------------------------
    # 3.) Initialise performance matrix for storing values:
    # ----------------------------------------------------

    perf_sum = pd.DataFrame(
        index=['R2_train', 'R2_test', 'RMSE_train', 'RMSE_test', 'MAPE_train', 'MAPE_test', 'R2_CV', 'RMSE_CV',
               'size_train', 'size_test', 'best_parameters', 'model', 'predictor_pretreatment', 'target_pretreatment',
               'no_predictors', 'gini', 'perm_imp_mean', 'perm_imp_std',
               'shap_train', 'shap_test', 'shap_compressed_train', 'shap_compressed_test', 'x_test', 'x_train',
               'y_test', 'y_train', 'test_predictions', 'test_targets'], columns=y_train.columns)
    # ---------------------------------------------------
    # 4.) Create loop to iterate through output variables:
    # ---------------------------------------------------

    for count, column in enumerate(np.arange(y_train.columns.shape[0])):
        # for count, column in enumerate(np.arange(1)): # quick execution for testing

        target_variable = y_train.columns[count]  # select output parameter for which model is to be fitted

        # Initialise pretreated data frames
        X_train_pretreated = x_train.copy()
        X_test_pretreated = x_test.copy()
        Y_train_pretreated = y_train[target_variable].copy()
        Y_test_pretreated = y_test[target_variable].copy()

        # Define name of categorical variables
        categorical_names = ['Operation (Batch/Continuous)', 'Catalyst', 'Scale', 'Agent_air', 'Agent_air + steam',
                             'Agent_other', 'Agent_oxygen', 'Agent_steam',
                             'Reactor_fixed bed', 'Reactor_fluidised bed', 'Reactor_other', 'Bed_alumina', 'Bed_N/A',
                             'Bed_olivine', 'Bed_other', 'Bed_silica']

        # Pretreat predictor variables:
        if predictor_pretreatment == 1:  # Drop rows with missing values and remove non-continuous predictors
            # Training data
            X_train_dropped = X_train_pretreated.drop(categorical_names, axis=1).copy()  # drop non-continuous variables
            X_train_dropped = X_train_dropped.dropna(axis=0)
            X_train_dropped_mask = ~X_train_pretreated.isna().any(
                axis=1)  # get mask to drop corresponding values from Y data frame - True to keep value, False to drop it
            Y_train_pretreated = Y_train_pretreated[
                X_train_dropped_mask]  # drop corresponding rows in Y data frame
            X_train_pretreated = X_train_dropped  # update pretreated data frame

            # Test data
            X_test_dropped = X_test_pretreated.drop(categorical_names, axis=1).copy()  # drop non-continuous variables
            X_test_dropped = X_test_dropped.dropna(axis=0)
            X_test_dropped_mask = ~X_test_pretreated.isna().any(
                axis=1)  # get mask to drop corresponding values from Y data frame - True to keep value, False to drop it
            Y_test_pretreated = Y_test_pretreated[
                X_test_dropped_mask]  # drop corresponding rows in Y data frame
            X_test_pretreated = X_test_dropped  # update pretreated data frame

        elif predictor_pretreatment == 2:  # Mean impute missing values and remove non-continuous predictors
            # Training data
            X_train_dropped = X_train_pretreated.drop(categorical_names,
                                                      axis=1).copy()  # drop non-continuous variables
            for column in X_train_dropped.columns[
                X_train_dropped.isnull().any()].tolist():  # go through list of missing column names
                X_train_dropped[column] = X_train_dropped[column].fillna(
                    X_train_dropped[column].mean())  # mean impute missing values
            X_train_pretreated = X_train_dropped  # update dataframe

            # Test data
            X_test_dropped = X_test_pretreated.drop(categorical_names, axis=1).copy()  # drop non-continuous variables
            for column in X_test_dropped.columns[
                X_test_dropped.isnull().any()].tolist():  # go through list of missing column names
                X_test_dropped[column] = X_test_dropped[column].fillna(
                    X_test_dropped[column].mean())  # mean impute missing values
            X_test_pretreated = X_test_dropped  # update dataframe

        elif predictor_pretreatment == 3:  # Drop rows with missing values and add categorical variables
            # Training data
            X_train_dropped = X_train_pretreated.dropna(axis=0).copy()
            X_train_dropped_mask = ~X_train_pretreated.isna().any(
                axis=1)  # get mask to drop corresponding values from Y data frame - True to keep value, False to drop it
            Y_train_pretreated = Y_train_pretreated[
                X_train_dropped_mask]  # drop corresponding rows in Y data frame
            X_train_pretreated = X_train_dropped  # update pretreated data frame

            # Test data
            X_test_dropped = X_test_pretreated.dropna(axis=0).copy()
            X_test_dropped_mask = ~X_test_pretreated.isna().any(
                axis=1)  # get mask to drop corresponding values from Y data frame - True to keep value, False to drop it
            Y_test_pretreated = Y_test_pretreated[
                X_test_dropped_mask]  # drop corresponding rows in Y data frame
            X_test_pretreated = X_test_dropped  # update pretreated data frame

        elif predictor_pretreatment == 4:  # Mean impute missing values and add categorical variables
            # Training data
            for column in X_train_pretreated.columns[
                X_train_pretreated.isnull().any()].tolist():  # go through list of missing column names
                X_train_pretreated[column] = X_train_pretreated[column].fillna(
                    X_train_pretreated[column].mean())  # mean impute missing values

            # Test data
            for column in X_test_pretreated.columns[
                X_test_pretreated.isnull().any()].tolist():  # go through list of missing column names
                X_test_pretreated[column] = X_test_pretreated[column].fillna(
                    X_test_pretreated[column].mean())  # mean impute missing values

        elif predictor_pretreatment == 5:  # KNN impute missing variables and add categorical variables
            # Training data
            KNN_imputer_train = KNNImputer(n_neighbors=3)
            X_train_pretreated = pd.DataFrame(KNN_imputer_train.fit_transform(X_train_pretreated))
            # Test data
            KNN_imputer_test = KNNImputer(n_neighbors=3)
            X_test_pretreated = pd.DataFrame(KNN_imputer_test.fit_transform(X_test_pretreated))
            # Note: Currently not working - Dataframe looks different to the way it is supposed to look after imputation - get in the same format as for the other methods
        else:
            print('Warning: Predictor pretreatment option invalid! Select an integer between 1 and 4 \n')

            # Pretreat target variables:
        if target_pretreatment == 1:  # drop rows with missing values present
            # Training data
            Y_train_dropped = Y_train_pretreated.dropna(axis=0)
            Y_train_dropped_mask = ~Y_train_pretreated.isna()  # get mask to drop corresponding values from X data frame - True to keep value, False to drop it
            X_train_pretreated = X_train_pretreated[
                Y_train_dropped_mask]  # drop corresponding rows in X data frame
            Y_train_pretreated = Y_train_dropped  # update pretreated data frame

        elif target_pretreatment == 2:  # Mean impute missing values
            Y_train_pretreated = Y_train_pretreated.fillna(
                Y_train_pretreated.mean())  # mean impute missing values

        elif target_pretreatment == 3:  # Impute missing values using random forest submodel
            # Training data
            XY_temp = pd.concat(
                [X_train_pretreated, X_test_pretreated])  # create dataframe with all inputs and considered target
            XY_temp[target_variable] = pd.concat([Y_train_pretreated, Y_test_pretreated])  # add target
            XY_temp = XY_temp.dropna()  # drop all rows with missing values for model training

            # Create temporary data sets for model training and testing
            x_RF_temp = XY_temp.drop([target_variable], axis=1)
            y_RF_temp = XY_temp[target_variable]

            # Create and fit model
            model_RF_temp = RandomForestRegressor(random_state=random_state)
            model_RF_temp.fit(x_RF_temp, y_RF_temp)

            # Make predictions and NaNs with predictions
            imputer_predictions = pd.DataFrame(model_RF_temp.predict(X_train_pretreated))
            target_array = Y_train_pretreated.to_numpy().flatten()  # extract target array with NaNs
            target_array[np.isnan(target_array)] = imputer_predictions.to_numpy().flatten()[
                np.isnan(target_array)]  # replace NaNs with predictions
            updated_tar_name = target_variable + "_imputed"
            Y_train_pretreated = pd.DataFrame(target_array)  # add output parameter to temporary data frame
            # Y_train_pretreated[updated_tar_name] = (target_array) # add output parameter to temporary data frame
            # Y_train_pretreated = Y_train_pretreated.drop([target_variable], axis=1) # drop old column
            Y_train_pretreated.columns = [target_variable]  # rename updated column to old name
            Y_train_pretreated = Y_train_pretreated.squeeze()  # turn variable back into a pandas Series object

        else:
            print('Warning: Target pretreatment option invalid!Select an integer between 1 and 3 \n')

        # Always treat target test data in the same way - i.e. do not make predicitons for missing values
        Y_test_dropped = Y_test_pretreated.dropna(axis=0)
        Y_test_dropped_mask = ~Y_test_pretreated.isna()  # get mask to drop corresponding values from X data frame - True to keep value, False to drop it
        X_test_pretreated = X_test_pretreated[Y_test_dropped_mask]  # drop corresponding rows in X data frame
        Y_test_pretreated = Y_test_dropped  # update pretreated data frame

        # -------------------------------------------------------------------------------------------------------------------
        # 5.) Check for missing values in data and select training and testing data.
        #     If missing values present - drop corresponding rows. Note: This should only be the case for missing target data
        #        in the test set as this should not be imputed/filled with any method. Flag warning if this is not the case.
        # -------------------------------------------------------------------------------------------------------------------

        if check_missing(X_train_pretreated) != 0 or check_missing(Y_train_pretreated) != 0 or check_missing(
                X_test_pretreated) != 0:
            print(
                'Warning: Missing values in x_train or x_test set. Missing values should only be present in y_test set')

        if modelname == 'XGBoost':  # update column names for XGBoost Model - cannot handle "[]" in column names

            if predictor_pretreatment == 1 or predictor_pretreatment == 2:
                X_train_pretreated.columns = ['C', 'H', 'S', 'PS', 'Ash', 'Moisture', 'Temp', 'ER']
                X_test_pretreated.columns = ['C', 'H', 'S', 'PS', 'Ash', 'Moisture', 'Temp', 'ER']
            else:
                X_train_pretreated.columns = ['C', 'H', 'S', 'PS', 'Ash', 'Moisture', 'Temp', 'Operation', 'ER', 'Cat',
                                              'Scale', 'agent_air',
                                              'agent_air_steam', 'agent_other', 'agent_oxygen', 'agent_steam',
                                              'reactor_fixed bed',
                                              'reactor_fluidised bed', 'reactor_other', 'bed_alumina', 'bed_na',
                                              'bed_olivine', 'bed_other', 'bed_silica']
                X_test_pretreated.columns = ['C', 'H', 'S', 'PS', 'Ash', 'Moisture', 'Temp', 'Operation', 'ER', 'Cat',
                                             'Scale', 'agent_air',
                                             'agent_air_steam', 'agent_other', 'agent_oxygen', 'agent_steam',
                                             'reactor_fixed bed',
                                             'reactor_fluidised bed', 'reactor_other', 'bed_alumina', 'bed_na',
                                             'bed_olivine', 'bed_other', 'bed_silica']

            Y_train_pretreated.columns = ['N2', 'H2', 'CO', 'CO2', 'CH4', 'C2Hn', 'LHV', 'Tar', 'Gas yield',
                                          'Char yield']
            Y_test_pretreated.columns = ['N2', 'H2', 'CO', 'CO2', 'CH4', 'C2Hn', 'LHV', 'Tar', 'Gas yield',
                                         'Char yield']

        # ------------------------------------------
        # 6.) Fit model and evaluate its performance:
        # ------------------------------------------
        # Random search of parameters, using 3 fold cross validation,
        # search across 100 different combinations, and use all available cores

        if optimisation == True:
            iterations_RandSearch = 10  # change back to 100 or go for proper grid search
            RandSearch_model = RandomizedSearchCV(estimator=model, param_distributions=param_grid,
                                                  n_iter=iterations_RandSearch,
                                                  cv=CV_folds, verbose=0, random_state=random_state)
            # Fit the random search model
            RandSearch_model.fit(X_train_pretreated, Y_train_pretreated)
            best_parameters = RandSearch_model.best_params_
            model = RandSearch_model.best_estimator_  # select best estimator as model for rest of code

        else:
            # fit model and make predictions
            model.fit(X_train_pretreated, Y_train_pretreated)
            best_parameters = 'default'  # note that default paramters have been used

        pickled_model = pickle.dumps(model)  # create storable instance of model
        y_train_pred = model.predict(X_train_pretreated)
        y_test_pred = model.predict(X_test_pretreated)

        # Evaluate performance - other performance measures can be shown with sorted(sklearn.metrics.SCORERS.keys())

        # R2
        R2_train = model.score(X_train_pretreated, Y_train_pretreated)
        R2_test = model.score(X_test_pretreated, Y_test_pretreated)

        # RMSE
        RMSE_train = mean_squared_error(Y_train_pretreated, y_train_pred, squared=False)
        RMSE_test = mean_squared_error(Y_test_pretreated, y_test_pred, squared=False)

        # MAPE
        MAPE_train = MAPE(Y_train_pretreated, y_train_pred)
        MAPE_test = MAPE(Y_test_pretreated, y_test_pred)

        # Noise variance - Currently results in division by zero which causes warning to be displayed - code still works
        # sqrt_noise_var_train = np.sqrt(noise_var(y_train_ready, y_train_pred, len(x_train_ready), len(x_train_ready)))
        # sqrt_noise_var_test = np.sqrt(noise_var(y_test_ready, y_test_pred, len(x_test_ready), len(x_train_ready)))

        # Evaluate cross validated performance on entire dataset

        # Combine datasets again before calculating cross validation scores
        x_complete = pd.concat([X_train_pretreated, X_test_pretreated])
        y_complete = pd.concat([Y_train_pretreated, Y_test_pretreated])

        # Calculate cross validated scores
        CV_R2_scores = cross_val_score(model, x_complete, y_complete, cv=CV_folds, scoring='r2')
        R2_CV = np.mean(CV_R2_scores)
        CV_RMSE_scores = -cross_val_score(model, x_complete, y_complete, cv=CV_folds,
                                          scoring='neg_root_mean_squared_error')
        RMSE_CV = np.mean(CV_RMSE_scores)

        # ---------------------------------------------------------
        # 7.) Compute feature importances using a range of methods:
        # ---------------------------------------------------------
        if modelname == 'RF' or modelname == 'GBR' or modelname == 'XGBoost' or modelname == 'AdaBoost':
            # 1.) Gini importance:
            gini_importances = model.feature_importances_

            # 2.) Permutation importance
            perm_importances = permutation_importance(model, X_test_pretreated, Y_test_pretreated, n_repeats=30,
                                                      random_state=random_state)
            perm_importances_mean = np.abs(perm_importances.importances_mean)
            perm_importances_std = np.abs(perm_importances.importances_std)

            if modelname == 'RF' or modelname == 'GBR' or modelname == 'XGBoost':
                # 3. SHAP importance
                shap_explainer = shap.TreeExplainer(model)
                shap_values_train = shap_explainer.shap_values(X_train_pretreated)
                shap_values_test = shap_explainer.shap_values(X_test_pretreated)

            elif modelname == 'AdaBoost':
                shap_values_train = 'not applicable for AdaBoost'
                shap_values_test = 'not applicable for AdaBoost'

        elif modelname == 'SVM' or modelname == 'ANN':  # feature importance not calculated for SVM or ANN
            gini_importances = 'not applicable for SVM or ANN'
            perm_importances_mean = 'not applicable for SVM or ANN'
            perm_importances_std = 'not applicable for SVM or ANN'
            shap_values_train = 'not applicable for SVM or ANN'
            shap_values_test = 'not applicable for SVM or ANN'

        # -------------------------------------------------------------------
        # 8.) Store performance indicators and other information in dataframe:
        # -------------------------------------------------------------------
        # Performance measure (R2, RMSE, etc)
        perf_sum.at['R2_train', target_variable] = R2_train
        perf_sum.at['R2_test', target_variable] = R2_test
        perf_sum.at['RMSE_train', target_variable] = RMSE_train
        perf_sum.at['RMSE_test', target_variable] = RMSE_test
        perf_sum.at['R2_CV', target_variable] = R2_CV
        perf_sum.at['RMSE_CV', target_variable] = RMSE_CV
        perf_sum.at['MAPE_train', target_variable] = MAPE_train
        perf_sum.at['MAPE_test', target_variable] = MAPE_test
        perf_sum.at['best_parameters', target_variable] = best_parameters
        # perf_sum.at['sqrt_noise_var_train', target_variable] = sqrt_noise_var_train
        # perf_sum.at['sqrt_noise_var_test', target_variable] = sqrt_noise_var_test

        # Model and other info
        perf_sum.at['model', target_variable] = pickled_model  # unpickle to load model again
        perf_sum.at['predictor_pretreatment', target_variable] = predictor_pretreatment
        perf_sum.at['target_pretreatment', target_variable] = target_pretreatment
        perf_sum.at['no_predictors', target_variable] = np.size(X_train_pretreated.columns)
        perf_sum.at['size_train', target_variable] = len(X_train_pretreated)
        perf_sum.at['size_test', target_variable] = len(X_test_pretreated)

        # Variable importance measures and related
        perf_sum.at['gini', target_variable] = gini_importances
        perf_sum.at['perm_imp_mean', target_variable] = perm_importances_mean
        perf_sum.at['perm_imp_std', target_variable] = perm_importances_std
        perf_sum.at['shap_train', target_variable] = shap_values_train
        perf_sum.at['shap_test', target_variable] = shap_values_test
        perf_sum.at['x_test', target_variable] = X_test_pretreated  # required to create shap plots and superlearner
        perf_sum.at['x_train', target_variable] = X_train_pretreated  # required to create shap plots and superlearner
        perf_sum.at['y_test', target_variable] = Y_test_pretreated  # required for superlearner
        perf_sum.at['y_train', target_variable] = Y_train_pretreated  # required for superlearner

        # Test prediction and true values
        perf_sum.at['test_predictions', target_variable] = y_test_pred
        perf_sum.at['test_targets', target_variable] = Y_test_pretreated

        # ---------------------------------------------------
        # 9.) Display model performance and other information at runtime:
        # ---------------------------------------------------
        if display == True:  # Choose whether to display figures and performance of model
            # Predicted variable and sample size
            print('Performance of model number %d for the output' % (count + 1), target_variable, ':\n')
            print('Number of samples in training set: %.1f \t Number of sample in test set: %.1f \n' % (
                len(X_train_pretreated), len(X_test_pretreated)))

            # R2
            print('\t Train R2: %.3f \n' % (R2_train))
            print('\t Test R2: %.3f\n' % (R2_test))
            print('\t CV R2: %.3f (+/- %.3f) \n' % (R2_CV, CV_R2_scores.std()))

            # RMSE
            print('\t Train RMSE: %.3f \n' % (RMSE_train))
            print('\t Test RMSE: %.3f\n' % (RMSE_test))
            print('\t CV RMSE: %.3f (+/- %.3f) \n' % (RMSE_CV, CV_RMSE_scores.std()))
            # MAPE
            print('\t Test MAPE: %.3f\n' % (MAPE_test))

            # -------------------
            # 10.) Plot model fit:
            # -------------------
            x_labels = [r'Target $N_{2}$ [vol. % db]',
                        r'Target $H_{2}$ [vol. % db]',
                        r'Target CO [vol. % db]',
                        r'Target $CO_{2}$ [vol. % db]',
                        r'Target $CH_{4}$ [vol. % db]',
                        r'Target $C_{2}H_{n}$ [vol. % db]',
                        r'Target LHV [MJ/$Nm^{3}$]',
                        r'Target Tar [g/$Nm^{3}$]',
                        r'Target Gas Yield [$Nm^{3}$/kg wb]',
                        r'Target Char Yield [g/kg wb]'
                        ]

            y_labels = [r'Predicted $N_{2}$ [vol. % db]',
                        r'Predicted $H_{2}$ [vol. % db]',
                        r'Predicted CO [vol. % db]',
                        r'Predicted $CO_{2}$ [vol. % db]',
                        r'Predicted $CH_{4}$ [vol. % db]',
                        r'Predicted $C_{2}H_{n}$ [vol. % db]',
                        r'Predicted LHV [MJ/$Nm^{3}$]',
                        r'Predicted Tar [g/$Nm^{3}$]',
                        r'Predicted Gas Yield [$Nm^{3}$/kg wb]',
                        r'Predicted Char Yield [g/kg wb]'
                        ]

            target_axis_string = x_labels[count]
            predicted_axis_string = y_labels[count]
            g = sns.JointGrid(x=Y_test_pretreated, y=y_test_pred)
            g.fig.set_figwidth(5)  # change fig width for publication
            g.fig.set_figheight(2.25)  # change fig height for publication
            sns.scatterplot(x=Y_train_pretreated, y=y_train_pred, s=100, color='orange', ax=g.ax_joint)
            sns.scatterplot(x=Y_test_pretreated, y=y_test_pred, s=100, color='blue', ax=g.ax_joint)
            # sns.regplot(x_source=Y_test_pretreated, y_source=y_test_pred, ax=g.ax_joint)
            g.set_axis_labels(target_axis_string, predicted_axis_string, fontsize=16, fontname='Arial')
            sns.histplot(x=Y_train_pretreated, ax=g.ax_marg_x, color='orange')
            sns.histplot(x=Y_test_pretreated, ax=g.ax_marg_x, color='blue')
            g.ax_marg_x.legend(['Train', 'Test'])
            plt.show()
            fig = g.fig  # get current seaborn axis as figure to save it
            fig.savefig(directory + '\Figures\\Scatter Plots\\' + modelname + '\\Scatter_target' + '_' + str(
                count + 1) + '.png', dpi=500, bbox_inches='tight')

        # --------------------------
        # 11.) Turn warnings back on:
        # --------------------------
        simplefilter('default', category=FutureWarning)  # turn depreciation warnings back on
        simplefilter('default', category=ConvergenceWarning)  # turn convergence warnings back on

        # ----------------------------------
        # 12.) Return outputs as a dataframe:
        # ----------------------------------

        if display == True:
            print(
                '# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # \n')

    return perf_sum


print('We are working')