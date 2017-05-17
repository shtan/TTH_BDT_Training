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
        self.BackgroundWeightExpression="Weight_XS*Weight_PU*Weight_CSV"



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
        #maxSig=self.getMaxSig(histo_effS,histo_effB)
        #SigSum=self.getSigSum(histo_effS,histo_effB)
        #logfile=open('log.txt','a')
        #header='-------------------------------------------------------------------------------------------------------------------------------------------------\n'
        #header+='%12s %12s %12s %16s %12s %12s %12s %12s %12s' % ('time [s]','N training','ROC integral','Brej(Seff=0.5)','max sign.','KS (S)','KS (B)','Ntrees','NVars')
        #if self.verbose:
            #print  header
        #if self.ntrainings==1:
            #logfile.write(header)
        #log1='%12.1f %12.0f %12.3f %16.3f %12.3f %12.2f %12.2f %12.0f %12.0f' % (self.stopwatch.RealTime(),self.ntrainings,rocintegral,bkgRej50,maxSig,ksS,ksB,ntrees+0.5,len(variables))
        #self.stopwatch.Start(False)        
        #log2="\n"+"\t".join(variables)+"\n"
        #log=log1+log2
        #if self.verbose:
            #print log
        #logfile.write(log)
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

        for var in variables+["Weight_XS","Weight_CSV","Weight_PU"]:
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

        for var in variables+["Weight_XS","Weight_CSV","Weight_PU"]:
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
	  
	  for var in variables+["Weight_XS","Weight_CSV","Weight_PU"]:
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
	  
	  for var in variables+["Weight_XS","Weight_CSV","Weight_PU"]:
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

    #def getMaxSig(self,histo_effS,histo_effB):
        #maxSig=-1
        #maxSigExp=-1
        #for i in range(histo_effS.GetNbinsX()):
            #effS=histo_effS.GetBinContent(i)
            #effB=histo_effB.GetBinContent(i)
            #sig=-1
            #if effS>0:
                #sig=effS*6.3/math.sqrt(effS*6.3+effB*33.6)
                ##sig=effS*self.nsignal/math.sqrt(effS*self.nsignal+effB*self.nbackground)
            #if sig>maxSig:
                #maxSig=sig
        #return maxSig
            
    #def getSigSum(self,histo_effS,histo_effB):
        #SigSum=0.0
        #for i in range(histo_effS.GetNbinsX()):
            #effS=histo_effS.GetBinContent(i)
            #effB=histo_effB.GetBinContent(i)
            #sig=0.0
            #if effS>0:
                #sig=effS*6.3/math.sqrt(effS*6.3+effB*33.6)
            #SigSum+=sig
        #return SigSum
        
    #def ROCandMaxSig(self,histoS, histoB):
        #nBins=histoS.GetNbinsX()
        #nBinsB=histoB.GetNbinsX()
        #integralS=histoS.Integral(0,nBins+1)
        #integralB=histoB.Integral(0,nBinsB+1)
        #x=array("d")
        #y=array("d")
        #maxSig=-1
        #x.append(0)
        #y.append(0)
        #for i in range(0,nBins+1):
            #effS=histoS.Integral(i,nBins)/integralS
            #effB=histoB.Integral(i,nBins)/integralB
            #sig=effS*self.nsignal/math.sqrt(effS*self.nsignal+effB*self.nbackground)
            #if sig>maxSig:
                #maxSig=sig
                ##        print effS
                ##        print effB
            #x.append(effS)
            #y.append(effB)
        #x.append(1)
        #y.append(1)
        #g = ROOT.TGraph(len(x), x,y)
        #return g,maxSig

    #def LorenzCurve(self,histoS, histoB):
        #nBins=histoS.GetNbinsX()
        #nBinsB=histoB.GetNbinsX()
        #integralS=histoS.Integral(0,nBins+1)
        #integralB=histoB.Integral(0,nBinsB+1)
        #x=array("d")
        #y=array("d")
        #x.append(0)
        #y.append(0)
        #for i in range(0,nBins+1):
            #effS=histoS.Integral(i,nBins)/integralS
            #effB=histoB.Integral(i,nBins)/integralB
            #effAll=(effS*self.nsignal+effB*self.nbackground)/(self.nsignal+self.nbackground)
            #x.append(effAll)
            #y.append(effS)
        #x.append(1)
        #y.append(1)
        #g = ROOT.TGraph(len(x), x,y)
    
        #return g

    #def remove_worst_until(self,length):
        #if(len(self.variables)<=length):
            #return 
        #else:
            #print "####### findig variable to remove, nvars is "+str(len(self.variables))+", removing until nvars is "+str(length)+"."
            #bestscore=-1.
            #bestvars=[]
            #worstvar=""
            #for i in range(len(self.variables)):
                ## sublist excluding variables i
                #sublist=self.variables[:i]+self.variables[i+1:]
                #score,ks, maxSig, bkgRej50, bkgRej50_training=self.run(sublist)
                #if score>bestscore:
                    #bestscore=score
                    #bestvars=sublist
                    #worstvar=self.variables[i]
            #print "####### removing ",
            #print worstvar
            #self.unusedvariables.append(worstvar)
            #self.variables=bestvars
            #self.remove_worst_until(length)

    #def add_best_until(self,length):
        #if(len(self.variables)>=length):
            #return
        #elif len(self.unusedvariables)==0:
            #return        
        #else:
            #print "####### findig variable to add, nvars is "+str(len(self.variables))+", adding until nvars is "+str(length)+"."
            #bestscore=-1.
            #bestvar=""
            #for var in self.unusedvariables:
                #newlist=self.variables+[var]
                #score,ks, maxSig, bkgRej50, bkgRej50_training=self.run(newlist)
                #if score>bestscore:
                    #bestscore=score
                    #bestvar=var
            #print "####### adding ",
            #print bestvar
            #self.unusedvariables.remove(bestvar)
            #self.variables=self.variables+[bestvar]
            #self.add_best_until(length)

    #def get_ranking_removebest(self):
        #print "####### Calculating ranking by iteratively removing best variable"
        #remainingvars=list(self.variables)
        #bestvars=[]
        #while len(remainingvars)>1:
            #worstscore=999999.
            #worstvars=[]
            #bestvar=""
            #for i in range(len(remainingvars)):
                #sublist=remainingvars[:i]+remainingvars[i+1:]
                #score,ks, maxSig, bkgRej50, bkgRej50_training=self.run(sublist)
                #if score<worstscore:
                    #worstscore=score
                    #worstvars=sublist
                    #bestvar=remainingvars[i]
            #bestvars.append(bestvar)
            #remainingvars=worstvars
        #bestvars.append(remainingvars[0])
        #print "####### Ranking"
        #position=0
        #for var in bestvars:
            #position+=1
            #print "####### "+str(position)+" : "+var
        #return bestvars

    #def get_ranking_removeworst(self):
        #print "####### Calculating ranking by iteratively removing worst variable"
        #remainingvars=list(self.variables)
        #worstvars=[]
        #while len(remainingvars)>1:
            #bestscore=-999999.
            #besttvars=[]
            #worstvar=""
            #for i in range(len(remainingvars)):
                #sublist=remainingvars[:i]+remainingvars[i+1:]
                #score,ks, maxSig, bkgRej50, bkgRej50_training=self.run(sublist)
                #if score>bestscore:
                    #bestscore=score
                    #bestvars=sublist
                    #worstvar=remainingvars[i]
            #worstvars.append(worstvar)
            #remainingvars=bestvars
        #worstvars.append(remainingvars[0])
        #print "####### Ranking"
        #position=0
        #bestvars=reversed(worstvars)
        #for var in bestvars:
            #position+=1
            #print "####### "+str(position)+" : "+var
        #return bestvars
        

    #def optimize_ntrees(self,factorlist=[0.3,0.5,0.7,1.,1.5,2.,3.]):
        #print "####### optimizing ntrees, starting value ",
        #print self.ntrees
        #ntreelist=[x * self.ntrees for x in factorlist] 
        #print "####### trying values ",
        #print ntreelist
        #bestn=ntreelist[0]
        #bestscore=-1
        #for n in ntreelist:
            #score,ks,maxSig, bkgRej50, bkgRej50_training=self.run(self.variables,n)
            #if score>bestscore and ks>0.05:
                #bestscore=score
                #bestn=n
        #print "####### optiminal value is ",
        #print bestn
        #self.ntrees=bestn
        #if bestn==ntreelist[-1] and len(ntreelist)>2:
            #print "####### optiminal value is highest value, optimizing again"
            #highfactorlist=[f for f in factorlist if f > factorlist[-2]/factorlist[-1]]
            #self.optimize_ntrees(highfactorlist)
        #if bestn==ntreelist[0]and len(ntreelist)>2:
            #print "####### optiminal value is lowest value, optimizing again"
            #lowfactorlist=[f for f in factorlist if f < factorlist[1]/factorlist[0]]            
            #self.optimize_ntrees(lowfactorlist)


    #def test_BDT_Parameters(self):
        #print self.variables
        #ntreelist=[500,1000,1500,2000,2500]
        #Shrinkagelist=[0.001, 0.003, 0.005, 0.007, 0.01]
        #BaggingFractionlist=[0.2, 0.5, 0.8]
        #nCutslist=[20, 40, 60]
        #maxDepthlist=[2,3]
        #ranking = [(0,)]*450
        ##print ranking
        #nloop=0
        #print "######## testing different parameter Settings"
        #for ntrees in ntreelist:
          #for shrinkage in Shrinkagelist:
            #for baggingfraction in BaggingFractionlist:
              #for nCuts in nCutslist:
                #for maxDepth in maxDepthlist:
                  #score,ks, maxSig, SigSum, bkgRej50, bkgRej50_training=self.run(self.variables, ntrees, shrinkage, baggingfraction, nCuts, maxDepth)
                  #bdtoption="NTrees="+str(ntrees)+":BoostType=Grad:Shrinkage="+str(shrinkage)+":UseBaggedGrad:GradBaggingFraction="+str(baggingfraction)+":nCuts="+str(nCuts)+":MaxDepth="+str(maxDepth)
                  ##print bdtoption
                  ##print "ROC-Integral "+str(score)
                  ##print "KS-Test "+str(ks)
                  ##print "-------------------------------------------------------------------------------------"
                  #print "step "+str(nloop)
                  #ranking[nloop]=(score,ks,maxSig,SigSum,bdtoption)
                  #nloop+=1
        #print "######## finished"
        #rankByScore = sorted(ranking, key=lambda s:s[0], reverse=True)
        #rankByKS = sorted(ranking, key=lambda s:s[1], reverse=True)
        #rankBymaxSig = sorted(ranking, key=lambda s:s[2], reverse=True)
        #rankBySigSum = sorted(ranking, key=lambda s:s[3], reverse=True)
        ##print "by Score"
        ##print rankByScore
        ##print "by KS"
        ##print rankByKS
        #f = open("ranking.txt" ,"w")
        #f.write("ranked by ROCI\n")
        #for element in rankByScore:
          #f.write(str(element)+"\n")
        #f.write("\n--------------------------------------------------\n")
        #f.write("ranked by KS\n")
        #for element in rankByKS:
          #f.write(str(element)+"\n")
        #f.write("\n--------------------------------------------------\n")
        #f.write("ranked by maxSig @ nSig=6.3 and nBkg=33.6 \n")
        #for element in rankBymaxSig:
          #f.write(str(element)+"\n")
        #f.write("\n--------------------------------------------------\n")
        #f.write("ranked by SigSum @ nSig=6.3 and nBkg=33.6 \n")
        #for element in rankBySigSum:
          #f.write(str(element)+"\n")
        #f.write("\n--------------------------------------------------\n")
        #f.close()
        #print "results have been written to ranking.txt"
        
        
    #def Find_best_BDT_Parameters(self):
        #print self.variables
        #ntreelist=[500, 1000, 1500, 2000, 2500]
        #Shrinkagelist=[0.001, 0.005, 0.008, 0.01]
        #BaggingFractionlist=[0.2, 0.5, 0.8]
        #nCutslist=[20, 40, 60, 80]
        #maxDepthlist=[2,3]
        
        #BestNTrees=0
        #BestShrinkage=0.0
        #BestBF=0.0
        #BestNCuts=0
        #BestMaxDepth=0
        #BestBDToptions=""
        #maxScore=0.0
        #maxKS=0.0
        
        ##print ranking
        #nloop=0
        #print "######## testing different parameter Settings"
        #for ntrees in ntreelist:
          #for shrinkage in Shrinkagelist:
            #for baggingfraction in BaggingFractionlist:
              #for nCuts in nCutslist:
                #for maxDepth in maxDepthlist:
                  #score,ks, maxSig, SigSum, bkgRej50, bkgRej50_training=self.run(self.variables, ntrees, shrinkage, baggingfraction, nCuts, maxDepth)
                  #bdtoption="NTrees="+str(ntrees)+":BoostType=Grad:Shrinkage="+str(shrinkage)+":UseBaggedGrad:GradBaggingFraction="+str(baggingfraction)+":nCuts="+str(nCuts)+":MaxDepth="+str(maxDepth)
                  #print score, ks
                  #if score > maxScore:
                    #if ks > 0.1:
                      #if ks > maxKS:
                        #BestNTrees=ntrees
                        #BestShrinkage=shrinkage
                        #BestBF=baggingfraction
                        #BestNCuts=nCuts
                        #BestMaxDepth=maxDepth
                        #BestBDToptions=bdtoption
                    
                  ##print bdtoption
                  ##print "ROC-Integral "+str(score)
                  ##print "KS-Test "+str(ks)
                  ##print "-------------------------------------------------------------------------------------"
                  #print "step "+str(nloop)
                  #nloop+=1
        #print "######## finished"
        #print "Best options"
        #print BestBDToptions
        #return BestNTrees, BestShrinkage, BestBF, BestNCuts, BestMaxDepth
        
