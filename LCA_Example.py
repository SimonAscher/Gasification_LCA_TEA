#%% Get model predictions
from functions.general.pred_distributions import get_all_prediction_distributions
from models.prediction_model import get_models, make_predictions
from models.prediction_model import fetch_inputs


all_pred_dists = get_all_prediction_distributions(make_predictions(models_dict=get_models(), data=fetch_inputs()))



"""
Work on this some more - how would LCA play out - 

processes

drying - 

syngas combustion - 

biochar soil application - 


"""








#%%
