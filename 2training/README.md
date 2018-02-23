# TTH_BDT_Training
scripts used for ttH BDT training

This setup expects ntuples split into even/Odd events and into the different analysis categories
-> PATHTONTUPLES
##################
e.g. 
ls PATHTONTUPLES
Category_43
Category_44

ls PATHTONTUPLES/Category_43
Even
Odd

ls PATHTONTUPLES/Category_43/Even
ttbar_220_nominal.root
ttHbb_14_nominal.root
########################################

If you have different ntuple names or data structure you need to edit OnlyTrain.py

Then you need a config file that describes the gradient boosting BDT -> see bdtconfigs for examples

to train do:
python OnlyTrain.py CATEORY NAMEFORTRAINING BDTCONFIGFILE PATHTONTUPLES test|train
e.g.
python OnlyTrain.py 43 Spring17v1 bdtconfigs/43_S17V2.txt /nfs/dust/cms/user/kelmorab/SplitTrees04102017 test

# fyi 
# with test|train you can specifiy that the ROC and KS are calculated using the test or the trainings data (even/odd)
# no reason to change that usually

