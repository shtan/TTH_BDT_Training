import ROOT
import math
from array import array
from subprocess import call
from mvautils import *
class Trainer:
    def __init__(self,signalpath ,backgroundpath,signalpathTest, backgroundpathTest, BDTOptions,variables,unusedvariables=[],verbose=False,weightfile="weights/weights.xml"):
        self.signalpath=signalpath
        self.backgroundpath=backgroundpath
        #self.nsignal=nsignal
        #self.nbackground=nbackground
        self.variables=variables
        self.unusedvariables=unusedvariables
        #self.ntrees=ntrees
        self.ntrainings=0
        self.verbose=verbose
        self.signalpath=signalpath
        self.backgroundpath=backgroundpath
        self.signalpathTest=signalpathTest
        self.backgroundpathTest=backgroundpathTest
        self.stopwatch=ROOT.TStopwatch()
        self.weightfile=weightfile
        self.BDTOptions=BDTOptions
        self.factoryoptions="!V:Silent:!Color:DrawProgressBar:AnalysisType=Classification:Transformations=I"
        self.setVerbose(verbose)
        #self.SignalWeightExpression="Weight_XS*Weight_ElectronSFID*Weight_MuonSFID*Weight_MuonSFIso*Weight_ElectronSFGFS*Weight_MuonSFHIP*Weight_pu69p2*Weight_CSV"
        #self.BackgroundWeightExpression="Weight_XS*Weight_ElectronSFID*Weight_MuonSFID*Weight_MuonSFIso*Weight_ElectronSFGFS*Weight_MuonSFHIP*Weight_pu69p2*Weight_CSV"
        self.SignalWeightExpression="Weight_XS*Weight_PU*Weight_CSV"
        self.BackgroundWeightExpression="Weight_CSV*Weight_PU*(0.001958064*(N_GenTopHad==1 && N_GenTopLep==1)+0.001001529*(N_GenTopLep==2 && N_GenTopHad==0)+0.01077*(N_GenTopHad==2 && N_GenTopLep==0))"



    def setFactoryOption(self, option):
        self.factoryoptions=replaceOption(option,self.factoryoptions)

    def setVerbose(self,v=True):
        self.verbose=v
        if self.verbose:
            self.setFactoryOption('!Silent')
        else:
            self.setFactoryOption('Silent')
    
    def useTransformations(self, b=True):
        # transformation make the training slower
        if b:
            self.setFactoryOption('Transformations=I;D;P;G,D')
        else:
            self.setFactoryOption('Transformations=I')

    def setWeightExpression(self, expS, expB):
        self.SignalWeightExpression=expS
        self.BackgroundWeightExpression=expB
        

    # run and evaluate bdt with a certain set of variables and a certain number of trees
    def run(self,varlist=[],BDTOptions="",name=""):   
        if varlist!=[]:
          self.variables=varlist
        if BDTOptions!="":
          self.BDTOptions=BDTOptions
        #ntrees=numberoftrees
        #if len(variables)==0:
            #variables=self.variables
        #if ntrees==-1:
            #ntrees=self.ntrees
        ## train a bdt
        #self.ntrainings=self.ntrainings+1
        #if self.ntrainings==1:
            #self.stopwatch.Start()
        #factoryoptions=""
        #if len(variables)==1:
            #factoryoptions="Transformations=I;D;P;G,D"
        #bdtoptions="NTrees="+str(int(ntrees+0.5))
        #if shrinkage>0.0:
            #bdtoptions=bdtoptions+":Shrinkage="+str(shrinkage)
        #if baggingfraction>0.0:
            #bdtoptions=bdtoptions+":GradBaggingFraction="+str(baggingfraction)
        #if nCuts>0:
            #bdtoptions=bdtoptions+":nCuts="+str(int(nCuts))
        #if MaxDepth>0:
            #bdtoptions=bdtoptions+":MaxDepth="+str(int(MaxDepth))
        self.trainBDT(self.variables,self.BDTOptions,self.factoryoptions,name="")
        # open result file
        f = ROOT.TFile("autotrain"+name+".root")
        # get mva distribution for signal and background
        histoS = f.FindObjectAny('MVA_BDTG_S')
        histoB = f.FindObjectAny('MVA_BDTG_B')
        histoTrainS = f.FindObjectAny('MVA_BDTG_Train_S')
        histoTrainB = f.FindObjectAny('MVA_BDTG_Train_B')
        histo_rejBvsS = f.FindObjectAny('MVA_BDTG_rejBvsS')
        histo_effBvsS = f.FindObjectAny('MVA_BDTG_effBvsS')
        histo_effS = f.FindObjectAny('MVA_BDTG_effS')
        histo_effB = f.FindObjectAny('MVA_BDTG_effB')

        histo_trainingRejBvsS = f.FindObjectAny('MVA_BDTG_trainingRejBvsS')
        
        tools = ROOT.TMVA.Tools.Instance()
        sep = tools.GetSeparation(histoS, histoB)
        tools.DestroyInstance()
        
        
        rocintegral=histo_rejBvsS.Integral()/histo_rejBvsS.GetNbinsX()
        rocintegral_training=histo_trainingRejBvsS.Integral()/histo_trainingRejBvsS.GetNbinsX()
        bkgRej50=histo_rejBvsS.GetBinContent(histo_rejBvsS.FindBin(0.5))
        bkgRej50_training=histo_trainingRejBvsS.GetBinContent(histo_trainingRejBvsS.FindBin(0.5))
        ksS=histoTrainS.KolmogorovTest(histoS)
        ksB=histoTrainB.KolmogorovTest(histoB)
       
        # return numbers describing quality of training
        print "ROC: "+str(rocintegral)
        print "Separation: "+str(sep)
        print "KS: "+str(min(ksS,ksB))
        return rocintegral,min(ksS,ksB), bkgRej50, bkgRej50_training
        
        
    def trainBDT(self,variables,bdtoptions,factoryoptions,name=""):
        fout = ROOT.TFile("autotrain"+name+".root","RECREATE")
        newbdtoptions=replaceOptions(self.BDTOptions,bdtoptions)
        #        defaultfactoryoptions="!V:Silent:!Color:!DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Classification"
        # transformations take some some time
        newfactoryoptions=replaceOptions(self.factoryoptions,factoryoptions)
        factory = ROOT.TMVA.Factory("TMVAClassification", fout,"V:!Silent:Color:DrawProgressBar:Transformations=I:AnalysisType=Classification")
        # add variables
        for var in variables:
#            if "blr" in str(var):
#              print "->->->->blr hack-> check trainerChain.py"
#              factory.AddVariable(str("Evt_blr_ETH_transformed:=min(max(Evt_blr_ETH_transformed,-10.0),20)"))
#            else: 
#              factory.AddVariable(str(var))
          factory.AddVariable(str(var))
        # add signal and background 
        #inputS = ROOT.TFile( self.signalpath )
        #inputB = ROOT.TFile( self.backgroundpath )          
        #treeS     = inputS.Get("MVATree")
        #treeB = inputB.Get("MVATree")
        
        treeS=ROOT.TChain("MVATree")
        treeS.Add(self.signalpath)
        treeB=ROOT.TChain("MVATree")
        treeB.Add(self.backgroundpath)
        print self.signalpath
        print self.backgroundpath
        if not (self.signalpathTest=="" or self.backgroundpathTest==""):
	  print "using extra test trees"
	  print self.signalpathTest
	  print self.backgroundpathTest
	  treeSTest=ROOT.TChain("MVATree")
	  treeSTest.Add(self.signalpathTest)
	  treeBTest=ROOT.TChain("MVATree")
	  treeBTest.Add(self.backgroundpathTest)

        treeS.SetBranchStatus("*",0)
        treeS.SetBranchStatus("Weight",1)
        #treeS.SetBranchStatus("Weight_PV",1)
        treeS.SetBranchStatus("Weight_CSV",1)
        treeS.SetBranchStatus("Weight_PU",1)
        treeS.SetBranchStatus("Weight_XS",1)
        treeS.SetBranchStatus("Evt_blr_ETH",1)
        #treeS.SetBranchStatus("MEM_p",1)
        #treeS.SetBranchStatus("MEM_p_sig",1)
        #treeS.SetBranchStatus("MEM_p_bkg",1)
        treeS.SetBranchStatus("N_GenTopHad",1)
        treeS.SetBranchStatus("N_GenTopLep",1)

        for var in variables+["Weight_XS","Weight_CSV","Weight_PU","N_GenTopLep","N_GenTopHad"]:
	  if ":=" in var:
	      continue
          treeS.SetBranchStatus(var,1)

        treeB.SetBranchStatus("*",0)
        treeB.SetBranchStatus("Weight",1)
        #treeB.SetBranchStatus("Weight_PV",1)
        treeB.SetBranchStatus("Weight_PU",1)
        treeB.SetBranchStatus("Weight_XS",1)
        treeB.SetBranchStatus("Evt_blr_ETH",1)
        #treeB.SetBranchStatus("MEM_p",1)
        #treeB.SetBranchStatus("MEM_p_sig",1)
        #treeB.SetBranchStatus("MEM_p_bkg",1)
        treeB.SetBranchStatus("N_GenTopHad",1)
        treeB.SetBranchStatus("N_GenTopLep",1)
        treeB.SetBranchStatus("Weight_CSV",1)

        for var in variables+["Weight_XS","Weight_CSV","Weight_PU","N_GenTopLep","N_GenTopHad"]:
	  if ":=" in var:
	      continue
          treeB.SetBranchStatus(var,1)


        if not (self.signalpathTest=="" or self.backgroundpathTest==""):
	  print "init extra trees"
	  treeSTest.SetBranchStatus("*",0)
	  treeSTest.SetBranchStatus("Weight",1)
	  #treeSTest.SetBranchStatus("Weight_PV",1)
	  treeSTest.SetBranchStatus("Weight_PU",1)
	  treeSTest.SetBranchStatus("Weight_XS",1)
	  treeSTest.SetBranchStatus("Evt_blr_ETH",1)
	  #treeSTest.SetBranchStatus("MEM_p",1)
	  #treeSTest.SetBranchStatus("MEM_p_sig",1)
	  #treeSTest.SetBranchStatus("MEM_p_bkg",1)
	  treeSTest.SetBranchStatus("N_GenTopHad",1)
          treeSTest.SetBranchStatus("N_GenTopLep",1)
	  treeSTest.SetBranchStatus("Weight_CSV",1)
	  
	  for var in variables+["Weight_XS","Weight_CSV","Weight_PU","N_GenTopLep","N_GenTopHad"]:
	    if ":=" in var:
	      continue
	    treeSTest.SetBranchStatus(var,1)

	  treeBTest.SetBranchStatus("*",0)
	  treeBTest.SetBranchStatus("Weight",1)
	  #treeBTest.SetBranchStatus("Weight_PV",1)
	  treeBTest.SetBranchStatus("Weight_PU",1)
	  treeBTest.SetBranchStatus("Weight_XS",1)
	  treeBTest.SetBranchStatus("Evt_blr_ETH",1)
	  ##treeBTest.SetBranchStatus("MEM_p",1)
	  #treeBTest.SetBranchStatus("MEM_p_sig",1)
	  #treeBTest.SetBranchStatus("MEM_p_bkg",1)
	  treeBTest.SetBranchStatus("N_GenTopHad",1)
          treeBTest.SetBranchStatus("N_GenTopLep",1)
	  treeBTest.SetBranchStatus("Weight_CSV",1)
	  
	  for var in variables+["Weight_XS","Weight_CSV","Weight_PU","N_GenTopLep","N_GenTopHad"]:
	    if ":=" in var:
	      continue
	    treeBTest.SetBranchStatus(var,1)

        #use this for even/odd splitted train/test Trees
        #inputSTest = ROOT.TFile( self.signalpathTest )
        #inputBTest = ROOT.TFile( self.backgroundpathTest )          
        #treeSTest     = inputSTest.Get("MVATree")
        #treeBTest = inputBTest.Get("MVATree")


        print treeS, treeB
        if not (self.signalpathTest=="" or self.backgroundpathTest==""):
	  print "test chains"
	  print treeSTest, treeBTest
        # use equal weights for signal and bkg ?
        signalWeight     = 1.
        backgroundWeight = 1.
        
        preparationString="SplitMode=Random:NormMode=EqualNumEvents:V:VerboseLevel=Verbose"
        factor=1.0
        nBtrainingsevents=treeB.GetEntries()
        if nBtrainingsevents>=500000:
	  print "WARNING Have A LOT of bkg Events: Limiting to 200000 events"
	  preparationString+=":nTrain_Signal=0:nTrain_Background=200000:nTest_Signal=0:nTest_Background=200000"
          factor=nBtrainingsevents/float(500000.0)
          #backgroundWeight=factor
          
        if not (self.signalpathTest=="" or self.backgroundpathTest==""):
	  factory.AddSignalTree( treeS, signalWeight ,ROOT.TMVA.Types.kTraining )
	  factory.AddBackgroundTree( treeB, backgroundWeight,ROOT.TMVA.Types.kTraining)
	  factory.AddSignalTree( treeSTest, signalWeight ,ROOT.TMVA.Types.kTesting  )
	  factory.AddBackgroundTree( treeBTest, backgroundWeight,ROOT.TMVA.Types.kTesting)
	else:
	  factory.AddSignalTree( treeS, signalWeight )
	  factory.AddBackgroundTree( treeB, backgroundWeight)
	  
	print self.SignalWeightExpression
	print self.BackgroundWeightExpression
	factory.SetBackgroundWeightExpression( self.BackgroundWeightExpression+"*"+str(factor) )
        factory.SetSignalWeightExpression( self.SignalWeightExpression )
        print self.SignalWeightExpression, self.BackgroundWeightExpression
        # make cuts
        mycuts = ROOT.TCut("")
        mycutb = ROOT.TCut("")
        
        # train and test all methods
        factory.PrepareTrainingAndTestTree( mycuts, mycutb,preparationString )
        #norm modes: NumEvents, EqualNumEvents
        factory.BookMethod( ROOT.TMVA.Types.kBDT, "BDTG",newbdtoptions )
        factory.TrainAllMethods()
        factory.TestAllMethods()
        factory.EvaluateAllMethods()
        fout.Close()
        call(['mv','weights/TMVAClassification_BDTG.weights.xml',self.weightfile])
