import ROOT
from evaluaterRun2 import Sample
import gc

def GetSampleScales(trainSamples=[], testSamples=[]):
  outSampleEval=[]
  for i,s in enumerate(testSamples):
    print "\n---------------------------------------"
    print "checking scales for sample"
    print testSamples[i].name
    print testSamples[i].path
    print trainSamples[i].path
    SumWtrain=0
    SumWtest=0
    TotalSum=0
    testTreeFile=ROOT.TFile(testSamples[i].path,"READ")
    testTree=testTreeFile.Get("MVATree")
    #print testTree
    htest=ROOT.TH1D("htest","htest",100,testTree.GetMinimum("Evt_HT")-1.0,testTree.GetMaximum("Evt_HT")+1)
    #print htest
    testTree.Draw("Evt_HT>>htest","Weight")
    #print htest
    print "eval ", htest.Integral()
    SumWtest=htest.Integral()
    
    trainTreeFile=ROOT.TFile(trainSamples[i].path,"READ")
    trainTree=trainTreeFile.Get("MVATree")
    #print trainTree
    htrain=ROOT.TH1D("htrain","htrain",100,trainTree.GetMinimum("Evt_HT")-1.0,trainTree.GetMaximum("Evt_HT")+1)
    #print htrain
    trainTree.Draw("Evt_HT>>htrain","Weight")
    #print htrain
    print "train ", htrain.Integral()
    SumWtrain=htrain.Integral()
    TotalSum=SumWtrain+SumWtest
    print testSamples[i].name, "Sum ", TotalSum
    if SumWtest>0:
      scale=TotalSum/SumWtest
    else:
      scale=0
    #print "scale for eval sample ", scale
    
    if testSamples[i].name in ["DiBoson","SingleT","WJets","ZJets","ttW","ttZ"]:
      scale=1.0
    print "scale for eval sample ", scale
    outSampleEval.append(Sample(testSamples[i].name, testSamples[i].path, testSamples[i].constraint, scale))
    testTreeFile.Close()
    trainTreeFile.Close()
  return outSampleEval
