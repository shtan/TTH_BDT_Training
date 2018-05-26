from trainerChain import Trainer
from evaluaterRun2 import Evaluater
from evaluaterRun2 import Systematic
from evaluaterRun2 import Sample
from subprocess import call
from SampleScaleGetter import *

import sys
import json

print len(sys.argv)
if len(sys.argv)<7 or len(sys.argv)>7:
  print "usage:"
  print "python TrainAndEval.py CATEGORY NAME FINALBDTCONFIG_FILE INPUTPATH [test | train]"
  print "\n"
  print "PERM = noreco, perm0, perm1, perm2, perm3"
  print "CATEGORY = for example 43 or 62 or DB or so "
  print "NAME = name of outputfiles "
  print "FINALBDTCONFIG_FILE = BDT config file e.g. see example files "
  print "INPUTPATH = path to input trees . Has to contain directories called Category_*/* "
  print "[test | train] = do Testing on test or trainings samples "
  print "\n output is out in ./output/"
  exit(0)
  
perm=sys.argv[1]
category=sys.argv[2]
name=sys.argv[3]
FinalBDTConfig=sys.argv[4]
TestOrTrainSwitch=sys.argv[6]
if TestOrTrainSwitch=="train" or TestOrTrainSwitch=="Train":
  doTestonTrain=True
elif TestOrTrainSwitch=="test" or TestOrTrainSwitch=="Test":
  doTestonTrain=False
else:
  doTestonTrain=None

AnaPath=sys.argv[5]
SubBDTConfig="NONE"

print category
print name
print FinalBDTConfig
print SubBDTConfig

if (category == '64'):
  channel = '6j4t'
elif (category == '63'):
  channel = '6j3t'
elif (category == '62'):
  channel = '6j2t'
else:
  channel = 'None'

call(["mkdir","weights/"+name])
call(["mkdir","weights/"+name+"/"+perm])

f = open("output/TrainAndEval_"+name+"_"+perm+".txt","w")

#evaluationPath=AnaPath+"/Category_"+category+"/Even/"
#trainingPath=AnaPath+"/Category_"+category+"/Odd/"
trainingPath=AnaPath
evaluationPath=AnaPath

if doTestonTrain==True:
  print "!!!!!!!!!!DOING EVALUATION ON TRAINING SAMPLE!!!!!!!!"
  evaluationPath=trainingPath
elif doTestonTrain==None:
  print "!!!!!!!!!!DOING SPLITTING OF TRAINING SAMPLE!!!!!!!!"
  evaluationPath="NONE"
  
variablesFinal=[]

FBDTConfigFile=open(FinalBDTConfig,"r")
FBDTConfigList=list(FBDTConfigFile)
#splitlist=FBDTConfigList[0].split(" ")
for line in FBDTConfigList:
   if "variables" in line:
     line=line.split("=",1)
     #print line
     line=line[1].strip().replace("\'","\"")
     print type(line), line
     variablesFinalbuffer=json.loads(line)
     #print variablesFinal
   if "BDTOptions" in line:
     line=line.split("=",1)
     print line
     FinalBDTOptions=line[1]
     print FinalBDTOptions
buffername="output/FinalBDT_Config_"+category+"_"+name+".txt"
call(['cp', './'+FinalBDTConfig,buffername])

f.write("TrainingsPath: "+trainingPath+"\n")
f.write("EvalPath: "+evaluationPath+"\n\n")

for var in variablesFinalbuffer:
  variablesFinal.append(str(var))

f.write("FinalBDT Variables:\n")
f.write(str(variablesFinal)+"\n\n")

#signal_pat = "ttHTobb*.root"
signal_pat = "ttHTo*.root"
#background_pat = "TT_Tune*.root"
#signal_pat = "*signal.root"
background_pat = "*background.root"

print "Training Final BDT"
#if evaluationPath=="NONE":
  #trainerFinal=Trainer(trainingPath+"ttHbb_*_nominal.root",trainingPath+"ttbar_*_nominal.root","","",FinalBDTOptions,variablesFinal,[],False,"weights/weights_Final_"+category+"_"+name+".xml")
if doTestonTrain==None:
  trainerFinal=Trainer(trainingPath+signal_pat,trainingPath+background_pat,perm,channel,"None",FinalBDTOptions,variablesFinal,[],False,"weights/"+name+"/"+perm+"/weights_"+category+".xml")
#else:
  #trainerFinal=Trainer(trainingPath+"ttHbb_*_nominal.root",trainingPath+"ttbar_*_nominal.root",evaluationPath+"ttHbb_*_nominal.root",evaluationPath+"ttbar_*_nominal.root",FinalBDTOptions,variablesFinal,[],False,"weights/weights_Final_"+category+"_"+name+".xml")
elif doTestonTrain==False:
  trainerFinal=Trainer(trainingPath+signal_pat,trainingPath+background_pat,perm,channel,"Test",FinalBDTOptions,variablesFinal,[],False,"weights/"+name+"/"+perm+"/weights_"+category+".xml")
elif doTestonTrain==True:
  trainerFinal=Trainer(trainingPath+signal_pat,trainingPath+background_pat,perm,channel,"Train",FinalBDTOptions,variablesFinal,[],False,"weights/"+name+"/"+perm+"/weights_"+category+".xml")
trainerFinal.useTransformations(False)

trainerFinal.run(variablesFinal,FinalBDTOptions)

f.write("FinalBDT Parameters:\n")
f.write(FinalBDTOptions+"\n\n")
f.close()


if doTestonTrain==True:
  autotrainsuffix="train"
elif doTestonTrain==None:
  autotrainsuffix="split"
else:
  autotrainsuffix="test"

infname="autotrain.root"
outfname="output/training_"+category+"_"+name+"_"+perm+"_"+autotrainsuffix+".root"
call(["cp",infname,outfname])
print "all done"

exit(0)
