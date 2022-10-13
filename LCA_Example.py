#%% Get model predictions
from functions.general.predictions_to_distributions import get_all_prediction_distributions
from models.prediction_model import get_models, make_predictions
from functions.general.utility import fetch_ML_inputs


all_pred_dists = get_all_prediction_distributions(make_predictions(models_dict=get_models(), data=fetch_ML_inputs()))



"""
Work on this some more - how would LCA play out - 

processes

drying - 

syngas combustion - 

biochar soil application - 


"""








#%%
