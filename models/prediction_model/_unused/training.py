# %% Get directory path
import os

directory = os.getcwd()
print('Directory path: ', directory)

# %% Import required libraries

# Import basic operations and plotting
import pandas as pd

# import numpy as np
# import math
# import pickle
# import seaborn as sns
# import matplotlib
# import matplotlib.pyplot as plt
# import scipy.stats as stats
#
# # Import filters to remove unnecessary warnings
# from warnings import simplefilter
# from sklearn.exceptions import ConvergenceWarning
#
# # Import error performance measure, preprocessing etc. from sklearn
# from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV, RandomizedSearchCV, RepeatedKFold, ParameterGrid
# from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score
# from sklearn.impute import KNNImputer
# # from sklearn.utils.fixes import loguniform
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, MinMaxScaler

# from sklearn.pipeline import make_pipeline
#
# # Import Machine Learning Models from sklearn and other libraries
# from sklearn.linear_model import LinearRegression
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.ensemble import GradientBoostingRegressor
# from sklearn.ensemble import AdaBoostRegressor
# from sklearn.tree import DecisionTreeRegressor
# from sklearn.neural_network import MLPRegressor
# from sklearn import svm
# from xgboost import XGBRegressor
# import mlens
# from mlens.ensemble import SuperLearner
#
# # Import feature importance assessment methods
# from sklearn.inspection import permutation_importance
# import shap

# %%  Import training and testing data

# Define files containing predictor and target variables
pred_file = directory + '\data\\' + '20220810_Dataset_Gasification_Ascher_predictors.csv'
tar_file = directory + '\data\\' + '20220810_Dataset_Gasification_Ascher_targets.csv'

# Import csv files as data frames
df_pred = pd.read_csv(pred_file)
df_tar = pd.read_csv(tar_file)

# %% Create data frames of continous/categorical only predictors

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

print('The continuous predictor variables are:', df_pred_cont.columns)

print('The categorical predictor variables are:', df_pred_cat.columns)

# %% Preprocessing and preparation of predictor data

# Define common parameters
random_state = 42

# Drop unrequired predictors and show data set
df_pred_dropped = df_pred.drop(
    ['ID', 'feed_type', 'N', 'O', 'feed_LHV', 'feed_VM', 'feed_FC', 'feed_shape', 'feed_cellulose',
     'feed_hemicellulose',
     'feed_lignin', 'operating_pressure', 'residence_time'], axis=1).copy()

# Update predictor variable names
df_pred_dropped.columns = ['C [%daf]', 'H [%daf]', 'S [%daf]', 'Particle size [mm]', 'Ash [%db]', 'Moisture [%wb]',
                           'Temperature [°C]', 'Operation (Batch/Continuous)', 'Steam/Biomass [wt/wt]', 'ER',
                           'Gasifying agent', 'Reactor type', 'Bed material', 'Catalyst', 'Scale']

# Drop "Steam/Biomass [wt/wt]" as there is too many missing values
if 'Steam/Biomass [wt/wt]' in df_pred_dropped.columns:  # ensures code does not break if the cell is run twice
    df_pred_dropped = df_pred_dropped.drop(['Steam/Biomass [wt/wt]'], axis=1)

# Show categories/values of categorical predictors
print('Categories/values of categorical predictors:')
print('Categories of "Operation (Batch/Continuous)" are:', df_pred_dropped['Operation (Batch/Continuous)'].unique())
print('Categories of "Reactor type" are:', df_pred_dropped['Reactor type'].unique())
print('Categories of "Bed material" are:', df_pred_dropped['Bed material'].unique())
print('Categories of "Scale" are:', df_pred_dropped['Scale'].unique(), '\n')

# Show number of NaN in Operation Mode column
print('Instances of NaN in "Operation (Batch/Continuous)" column:',
      sum(pd.isna(df_pred_dropped['Operation (Batch/Continuous)'])))
print('For comparison, the number of instances of the two categories are shown for:')
print(df_pred_dropped.groupby(['Operation (Batch/Continuous)']).size(), '\n')

# Fix missing values in the form of NaN in "Operation (Batch/Continuous)" colum before ordinally encoding.
# Since few values are missing and continuous is dominant fill them with the most frequent category (i.e. continuous):
df_pred_preprocessed = df_pred_dropped.copy()   # create new data frame with preprocessed predictors - make sure it is a copy not a reference to original one
df_pred_preprocessed['Operation (Batch/Continuous)'] = df_pred_preprocessed['Operation (Batch/Continuous)'].fillna(
    df_pred_preprocessed['Operation (Batch/Continuous)'].mode().iloc[0])
print('Updated categories of "Operation (Batch/Continuous)" are:',
      df_pred_preprocessed['Operation (Batch/Continuous)'].unique())

# Ordinally encode Operation Mode and System Scale as they only have 2 categories
encoder_ordinal = OrdinalEncoder()
df_pred_preprocessed[['Operation (Batch/Continuous)', 'Scale']] = encoder_ordinal.fit_transform(
    df_pred_preprocessed[['Operation (Batch/Continuous)', 'Scale']])
# Show encoded categories
print('New categories of "Operation (Batch/Continuous)" are:',
      df_pred_preprocessed['Operation (Batch/Continuous)'].unique())
print('New categories of "Scale" are:', df_pred_preprocessed['Scale'].unique(), '\n')

# Check and preprocess categorical predictors with more than 2 categories before One Hot encoding

# Preprocess bed material column as missing values are present

# Show categories in "Bed material" column before preprocessing
print('Categories in "Bed material" column before preprocessing:')
print(df_pred_dropped['Bed material'].value_counts(), '\n')

# Turn categories with very few instances into category "other"
df_pred_preprocessed['Bed material'] = df_pred_preprocessed['Bed material'].replace(
    {'calcium oxide': 'other', 'dolomite': 'other'})

# Turn NaN into not applicable (n/a) as these represent fixed bed gasifiers
df_pred_preprocessed['Bed material'] = df_pred_preprocessed['Bed material'].fillna('N/A')

# Show updated values in Bed material's column
print('Updated categories in "Bed material" column after preprocessing:')
print(df_pred_preprocessed['Bed material'].value_counts(), '\n')

# Show categories in "Reactor type" and "Gasifying agent" column before One Hot encoding
print('Categories in "Reactor type" column:')
print(df_pred_dropped['Reactor type'].value_counts(), '\n')

print('Categories in "Gasifying agent" column:')
print(df_pred_dropped['Gasifying agent'].value_counts())

# One Hot Encode 'Gasifying agent', 'Reactor type', and 'Bed material'
df_pred_encoded = pd.get_dummies(df_pred_preprocessed, columns=['Gasifying agent', 'Reactor type', 'Bed material'],
                                 prefix=['Agent', 'Reactor', 'Bed'])

# %% Drop unrequired targets and show data set
if 'CGE' and 'CCE' in df_tar.columns:  # ensures code does not break if the cell is run twice
    df_tar_encoded = df_tar.drop(['CGE', 'CCE'], axis=1).copy()

# Update target variable names
df_tar_encoded.columns = ['N2 [vol.% db]', 'H2 [vol.% db]', 'CO [vol.% db]', 'CO2 [vol.% db]', 'CH4 [vol.% db]',
                          'C2Hn [vol.% db]',
                          'LHV [MJ/Nm3]', 'Tar [g/Nm3]', 'Gas yield [Nm3/kg wb]', 'Char yield [g/kg wb]']
