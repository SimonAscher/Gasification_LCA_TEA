import pickle
from warnings import simplefilter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score, train_test_split, RandomizedSearchCV, ParameterGrid
from sklearn.preprocessing import OrdinalEncoder


# %%
# Define prerequisite functions used within model builder function:

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


# %% Get directory path and import training and testing data
import os

directory = os.getcwd()

# Define files containing predictor and target variables
pred_file = directory + '\data\\' + '20220810_Dataset_Gasification_Ascher_predictors.csv'
tar_file = directory + '\data\\' + '20220810_Dataset_Gasification_Ascher_targets.csv'

# Import csv files as data frames
df_pred = pd.read_csv(pred_file)
df_tar = pd.read_csv(tar_file)

# Create data frames of continuous/categorical only predictors

df_pred_cont = df_pred.drop(['ID', 'feed_type', 'feed_shape', 'operating_condition', 'gasifying_agent',
                             'reactor_type', 'bed_material', 'catalyst', 'scale'],
                            axis=1)  # df of continuous predictors
df_pred_cont = df_pred_cont.drop(['feed_cellulose', 'feed_hemicellulose', 'feed_lignin', 'operating_pressure',
                                  'residence_time'], axis=1)  # drop variables with too many NaN
df_pred_cont.columns = ['C', 'H', 'N', 'S', 'O', 'LHV', 'PS', 'Ash',
                        'M', 'VM', 'FC', 'T', 'SB', 'ER']  # change column names for plotting

df_pred_cat = df_pred.drop(['ID', 'feed_particle_size', 'feed_LHV', 'C', 'H', 'N', 'S', 'O', 'feed_ash',
                            'feed_moisture', 'temperature', 'ER', 'steam_biomass_ratio'],
                           axis=1)  # df of categorical predictors

# %% Preprocessing of original predictor data (now target data)

# Drop unrequired predictors and show data set
df_pred_dropped = df_pred.drop(
    ['ID', 'feed_type', 'N', 'O', 'feed_LHV', 'feed_VM', 'feed_FC', 'feed_shape', 'feed_cellulose',
     'feed_hemicellulose', 'feed_lignin', 'operating_pressure', 'residence_time'],
    axis=1).copy()

# Update predictor variable names
df_pred_dropped.columns = ['C [%daf]', 'H [%daf]', 'S [%daf]', 'Particle size [mm]', 'Ash [%db]', 'Moisture [%wb]',
                           'Temperature [°C]', 'Operation (Batch/Continuous)', 'Steam/Biomass [wt/wt]', 'ER',
                           'Gasifying agent', 'Reactor type', 'Bed material', 'Catalyst', 'Scale']

# Drop "Steam/Biomass [wt/wt]" as there is too many missing values
df_pred_dropped = df_pred_dropped.drop(['Steam/Biomass [wt/wt]'], axis=1)

# Fix missing values in the form of NaN in "Operation (Batch/Continuous)" column before ordinally encoding.
# Since few values are missing and continuous is dominant fill them with the most frequent category (i.e. continuous):
df_pred_preprocessed = df_pred_dropped.copy()  # create new data frame with preprocessed predictors - make sure it is a copy not a reference to original one
df_pred_preprocessed['Operation (Batch/Continuous)'] = df_pred_preprocessed['Operation (Batch/Continuous)'].fillna(
    df_pred_preprocessed['Operation (Batch/Continuous)'].mode().iloc[0])

# Ordinally encode Operation Mode and System Scale as they only have 2 categories
encoder_ordinal = OrdinalEncoder()
df_pred_preprocessed[['Operation (Batch/Continuous)', 'Scale']] = encoder_ordinal.fit_transform(
    df_pred_preprocessed[['Operation (Batch/Continuous)', 'Scale']])

# Check and preprocess categorical predictors with more than 2 categories before One Hot encoding
# Preprocess bed material column as missing values are present
# Turn categories with very few instances into category "other"
df_pred_preprocessed['Bed material'] = df_pred_preprocessed['Bed material'].replace(
    {'calcium oxide': 'other', 'dolomite': 'other'})

# Turn NaN into not applicable (n/a) as these represent fixed bed gasifiers
df_pred_preprocessed['Bed material'] = df_pred_preprocessed['Bed material'].fillna('N/A')

# One Hot Encode 'Gasifying agent', 'Reactor type', and 'Bed material'
df_pred_encoded = pd.get_dummies(df_pred_preprocessed, columns=['Gasifying agent', 'Reactor type', 'Bed material', ],
                                 prefix=['Agent', 'Reactor', 'Bed'])

# Drop unrequired targets and show data set
df_tar_encoded = df_tar.drop(['CGE', 'CCE'], axis=1).copy()

# Update target variable names
df_tar_encoded.columns = ['N2 [vol.% db]', 'H2 [vol.% db]', 'CO [vol.% db]', 'CO2 [vol.% db]', 'CH4 [vol.% db]',
                          'C2Hn [vol.% db]', 'LHV [MJ/Nm3]', 'Tar [g/Nm3]', 'Gas yield [Nm3/kg wb]',
                          'Char yield [g/kg wb]']


# Create one function which can fit any of the considered models with an range of possible pretreatment options
def build_models(X, Y, modelname='RF', random_state=42, CV_folds=5,
                 optimisation=False, iterations_RandSearch='auto', display=True):
    """
    Function to train and test 'N' models for 'N' output/target variables (i.e. one model is trained for each
        ouput variable).
    A number of different ML algorithms are supported and may be defined by the variable 'modelname'.

    Inputs:
    X - predictor data for model training and testing
    Y - target data for model training and testing(multiple target columns possible)
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

    # 1.) Select which ML model is to be used and define parameter grids for hyperparameter optimisation:
    if modelname == 'RF':  # Use sklearn random forest regressor
        model = RandomForestRegressor(random_state=random_state)

        # Define grid/randomised search parameters
        max_depth = [int(x) for x in np.linspace(10, 100, num=10)]
        max_depth.append(None)

        param_grid = {
            'n_estimators': [10, 50, 100, 200, 500, 1000, 2000],
            'max_features': [1.0, 'sqrt'],
            'max_depth': max_depth,
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
        }

    elif modelname == 'GBR':  # Use sklearn gradient boosting regressor
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

    else:
        print('Error: Model name not defined!')

    if optimisation == True:
        parameter_combinations = len(ParameterGrid(param_grid))

        # Define number of iterations if 'auto' has been selected and no manual numerical input
        # Consider 25% of all possible parameter combinations in optimisation or at least 100
        if iterations_RandSearch == 'auto':
            iterations_RandSearch = int(parameter_combinations * 0.25)
            if iterations_RandSearch < 100:
                iterations_RandSearch = 100

            if iterations_RandSearch > 1000:  # set maximum number of iterations to 1000
                iterations_RandSearch = 1000

    # 2.) Split data into train and test sets:
    test_fraction = 0.15
    x_train, x_test, y_train, y_test = train_test_split(Y, X, test_size=test_fraction, random_state=random_state)

    # 3.) Initialise performance matrix for storing values:
    perf_sum = pd.DataFrame(
        index=['R2_train', 'R2_test', 'RMSE_train', 'RMSE_test', 'MAPE_train', 'MAPE_test', 'R2_CV', 'RMSE_CV',
               'size_train', 'size_test', 'best_parameters', 'model',
               'no_predictors', 'gini', 'perm_imp_mean', 'perm_imp_std',
               'shap_train', 'shap_test', 'shap_compressed_train', 'shap_compressed_test', 'x_test', 'x_train',
               'y_test', 'y_train', 'test_predictions', 'test_targets'], columns=y_train.columns)

    # 4.) Create loop to iterate through output variables:
    for count, column in enumerate(np.arange(y_train.columns.shape[0])):
        target_variable = y_train.columns[count]  # select output parameter for which model is to be fitted

        # Initialise pretreated data frames
        X_train_pretreated = x_train.copy()
        X_test_pretreated = x_test.copy()
        Y_train_pretreated = y_train[target_variable].copy()
        Y_test_pretreated = y_test[target_variable].copy()

        # Pre-treat PREDICTORS VARIABLES - Drop rows with missing values and add categorical variables
        X_train_dropped = X_train_pretreated.dropna(axis=0).copy()
        X_train_dropped_mask = ~X_train_pretreated.isna().any(
            axis=1)  # get mask to drop corresponding values from Y data frame - True to keep value, False to drop it
        Y_train_pretreated = Y_train_pretreated[X_train_dropped_mask]  # drop corresponding rows in Y data frame
        X_train_pretreated = X_train_dropped  # update pretreated data frame

        # Test data
        X_test_dropped = X_test_pretreated.dropna(axis=0).copy()
        X_test_dropped_mask = ~X_test_pretreated.isna().any(
            axis=1)  # get mask to drop corresponding values from Y data frame - True to keep value, False to drop it
        Y_test_pretreated = Y_test_pretreated[X_test_dropped_mask]  # drop corresponding rows in Y data frame
        X_test_pretreated = X_test_dropped  # update pretreated data frame

        # Pre-treat TARGET VARIABLES - Impute missing values using random forest submodel.
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

        # Always treat target test data in the same way - i.e. do not make predicitons for missing values
        Y_test_dropped = Y_test_pretreated.dropna(axis=0)
        Y_test_dropped_mask = ~Y_test_pretreated.isna()  # get mask to drop corresponding values from X data frame - True to keep value, False to drop it
        X_test_pretreated = X_test_pretreated[Y_test_dropped_mask]  # drop corresponding rows in X data frame
        Y_test_pretreated = Y_test_dropped  # update pretreated data frame

        # 5.) Check for missing values in data and select training and testing data.
        if check_missing(X_train_pretreated) != 0 or check_missing(Y_train_pretreated) != 0 or check_missing(
                X_test_pretreated) != 0:
            print(
                'Warning: Missing values in x_train or x_test set. Missing values should only be present in y_test set')

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
        perf_sum.at['x_train', target_variable] = X_train_pretreated  # required to creae shap plots and superlearner
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

            # 10.) Plot model fit:
            fig, ax = plt.subplots()
            ax.scatter(x=Y_train_pretreated, y=y_train_pred, s=100, color='orange', label="Train")
            ax.scatter(x=Y_test_pretreated, y=y_test_pred, s=100, color='blue', label="Test")
            plt.title(target_variable)
            plt.tight_layout()
            plt.show()
            fig.savefig(directory + '\Figures\\Scatter Plots\\' + modelname + '\\Scatter_target' + '_' + str(
                count + 1) + '.png', dpi=500, bbox_inches='tight')

        # --------------------------
        # 11.) Turn warnings back on:
        # --------------------------
        simplefilter('default', category=FutureWarning)  # turn depreciation warnings back on
        simplefilter('default', category=ConvergenceWarning)  # turn convergence warnings back on

    return perf_sum


# Show performance of model with the highest cross validated R2
RF_performance_summary_opt = build_models(df_pred_encoded, df_tar_encoded, modelname='RF', random_state=42, CV_folds=5,
                                          optimisation=True, iterations_RandSearch='auto', display=True)

# GBR_performance_summary_opt = build_models(df_pred_encoded, df_tar_encoded, modelname='GBR', random_state=42,
#                                            CV_folds=5, optimisation=True, iterations_RandSearch=1000,
#                                            display=True)
