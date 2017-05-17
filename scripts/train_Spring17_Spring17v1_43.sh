#!/bin/bash
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
cd /nfs/dust/cms/user/kelmorab/CMSSW_7_4_15/src
eval `scram runtime -sh`
cd /nfs/dust/cms/user/kelmorab/Spring17Training/3makeHistosAndCards
python OnlyTrain.py 43 Spring17v1 bdtconfigs/Spring17v1/43_S17V1.txt /nfs/dust/cms/user/kelmorab/SplitTrees2702_Spring17_V3 test