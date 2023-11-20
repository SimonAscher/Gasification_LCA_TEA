# A Model for the Rapid Assessment of the Environmental and Economic Impacts of Biomass and Waste Gasification Schemes

## Summary:
This work presents a framework to conduct **life cycle assessment (LCA)** and **techno-economic analysis (TEA)** of 
biomass and waste gasification schemes. Machine learning (ML), in the form of a **gradient boosting** model, is utilised to 
predict the composition and yields of gasification products. Uncertainties resulting from the machine learning model 
and other uncertainties throughout the model framework are accounted for through **Monte Carlo simulation** methodology.

## How to use the model:
### 1. Graphical user interface (GUI)
A convenient GUI, powered by [streamlit](https://streamlit.io/), has been implemented to run the model. This means no 
prior coding experience is required to run the model. The GUI can be accessed here: TODO: ADD LINK HERE

### 2. Write your own script 
Alternatively, a model can be implemented in python, where the developed methods can be used to construct a more 
personalised model. An example of this can be found in the file `simulation_example.py`. The model uses background data
(stored in `configs/default_settings.toml`) which can easily be expanded with case specific data (e.g. country specific
carbon intensity of electricity). Furthermore, a `.toml` file with case specific user inputs, such as feedstock 
properties and gasification conditions, can be generated manually or by using the GUI. One has to ensure that the 
case specific user input `.toml` is added to `configs/user_inputs` and the file is loaded by `config.py`.

All methods implemented in the library have extensive documentation. The following directories contain the key working parts of the model:
- `configs`: Contains settings files to load background data and user inputs which will be used in the model. 
- `data`: Contains data which is used to construct models etc.
- `functions`: Contains various functions used throughout the analysis. Mainly functions used for (i) the LCA, (ii) the 
TEA, (iii) the Monte Carlo simulation, (iv) general helper and utility functions.
- `gui`: Contains scripts to run the GUI.
- `models`: Contains the ML model to predict the yields and composition of gasification products.
- `objects`: Contains the classes underpinning the overarching simulation framework. In short, the following main
types of objects are used:
  - `Results`: Stores the results of a simulation run/case study and allows for the visualisation of the contained 
  results. `Results` objects are made up of a range of `Process` objects which make up the overall system boundary of
  a given scheme.
  - `Process`: Contains all process data for a given process (e.g. syngas combustion or biochar use). `Process` objects
  contain `GlobalWarmingPotential` and `CostBenefit` objects which in turn store the process' environmental and 
  economic impacts.
  - `Requirements`: This object type is stored and associated with a given `Process` object. A requirement has either
  (or both) an environmental or economic impact. Thus, `Requirements` objects are used to initialise 
  `GlobalWarmingPotential` and `CostBenefit` objects. `Requirements` can either have direct impacts 
  (e.g. `FossilGWP` and `PresentValue`) or indirect impacts (e.g. `Electricity` and `Oxygen`).
- `processes`: Contains process models for the various subprocesses making up a gasification scheme. All processes have 
default options which the model will revert to unless the user specifies alternative inputs.

## Life cycle assessment (LCA):
Life cycle assessment (LCA) is a widely recognised method to assess the environmental impacts of a product, service, or 
system throughout its entire life cycle.
- The LCA uses a **functional unit (FU)** of 1 tonne of feedstock treated.
- The LCA focuses on the impact category **global warming potential (GWP)** (also known as a carbon footprint) which is 
  measured in kg CO<sub>2-eq.</sub>/FU.

## Techno-economic analysis (TEA):
Techno-economic analysis (TEA) aims to analyse the economic performance of a product, service, or 
system. Here, two methods are implemented to assess the economic performance of a biomass or waste gasification scheme.
1. The net present value (NPV) method is used, where all future cash flows over a project's life span are 
discounted to the present. 
2. The benefit-cost ratio (BCR) method is used as a profitability indicator, which shows the relationship between a 
project's relative benefits and costs. A project with a BCR > 1 is considered economically feasible and is expected to 
deliver a positive net-present value. The opposite is true for a project with a BCR < 1.

The following convention is adopted for both types of analysis:
- Benefits are considered as positive (+ve) cash flows.
- Costs are considered as negative (-ve) cash flows.
