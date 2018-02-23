import ROOT
from array import array
from subprocess import call
from particle import Particle
from QueHelper import QueHelper
import time as timer
import sys
import json

class PSOManager:
    def __init__(self,Path="",Verbose=True,PSOConfig=""):
      self.Verbose=Verbose
      self.vw=1.0
      self.vp=1.0
      self.vg=1.0
      self.Particles=[]
      self.BestFOMGlobal=0.0
      self.BestKSGlobal=0.0
      self.BestCoordinatesGlobal=[]
      self.Coordinates=[]

      self.rand=ROOT.TRandom3(0) ## change to !=0 if you want repeatable random seeds
      self.Path=Path
      self.nParticles=10
      self.TenBestMVAs=[[0.0,0.0,"",[],[],[]] for i in range(10)]
      #print self.TenBestMVAs
      self.KSThreshold=0.1
      RunSystem="EKPSL5"
      self.NIterations=1
      self.FOM="ROCIntegral"
      self.MaxVariablesInCombination=10
      self.ImprovementThreshold=1.00
      self.FactoryString=""
      self.PreparationString=""
      self.SignalWeightExpression=""
      self.BackgroundWeightExpression=""
      self.MethodType="TMVA::Types::kBDT"
      self.MethodParams=""
      self.SignalTreeName="MVATree"
      self.BackgroundTreeName="MVATree"
      self.RepeatTrainingNTimes=0
      self.DrawNRandomAsStartingVars=0
      self.SaveTrainingsToTrees="False"
      self.UseEvenOddSplitting=0
      
      initialVariables=[]
      additionalVariables=[]
      ivars=[]
      avars=[]
      weightVariables=[]
      configFile=open(PSOConfig,"r")
      configLines=list(configFile)
      configFile.close()
      for i,l in enumerate(configLines):
        configLines[i]=configLines[i].replace("\n","")

      if "InitialVariables:" in configLines and "EndVariables" in configLines:
        id1=configLines.index("InitialVariables:")
        id2=configLines.index("EndVariables")
        initialVariables=configLines[id1+1:id2]
        configLines=configLines[:id1]+configLines[id2+1:]
      if "AdditionalVariables:" in configLines and "EndVariables" in configLines:
        id1=configLines.index("AdditionalVariables:")
        id2=configLines.index("EndVariables")
        additionalVariables=configLines[id1+1:id2]
        configLines=configLines[:id1]+configLines[id2+1:]

      if len(initialVariables)>0:
        for i, var in enumerate(initialVariables):
          if "#" in var:
            continue
          v=json.loads(var)
          ivars.append(str(v[0]))
      if len(additionalVariables)>0:
        for i, var in enumerate(additionalVariables):
          if "#" in var:
            continue
          v=json.loads(var)
          avars.append(str(v[0]))
      #check the input variables
      print "inital Variables ", len(ivars), ivars
      print "additional Variables ", len(avars), avars
      allVars=avars+ivars
      for var1 in allVars:
        counter=0
        for var2 in allVars:
          if var1==var2:
            counter+=1
          if counter>=2:
            print "ERROR: input variables defined multiple times"
            print var1
            exit(1)

      self.usedVariables=ivars
      self.unusedVariables=avars
      #self.TenBestMVAs[0]=(0.0,0.0,0.0,0.0,0.0,0,2,self.usedVariables, self.unusedVariables)
      #done with variables
      #read the rest of the stuff
      for line in configLines:
        if "#" in line:
          continue
        if "RunOn" in line:
          RunSystem=line.split("=",1)[1]
        if "NParticles" in line:
          self.nParticles=int(line.split("=",1)[1])
        if "NIterations" in line:
          self.NIterations=int(line.split("=",1)[1])
        if "wIneratia" in line:
          self.vw=float(line.split("=",1)[1])
        if "wMemory" in line:
          self.vp=float(line.split("=",1)[1])
        if "wSwarm" in line:
          self.vg=float(line.split("=",1)[1])
        if "FOM=" in line:
          self.FOM=line.split("=",1)[1]
        if "KSThreshold" in line:
          self.KSThreshold=float(line.split("=",1)[1])
        if "MaxVariablesInCombination" in line:
          self.MaxVariablesInCombination=int(line.split("=",1)[1])
        if "ImprovementThreshold" in line:
          self.ImprovementThreshold=float(line.split("=",1)[1])
        if "FactoryString" in line:
          self.FactoryString=line.split("=",1)[1]
        if "PreparationString" in line:
          self.PreparationString=line.split("=",1)[1]
        if "nTrain_Signal" in line:
          buff=line.split("=",1)[1]
          if buff!="" and buff!=" ":
            self.PreparationString="nTrain_Signal="+buff+":"+self.PreparationString
        if "nTrain_Background" in line:
          buff=line.split("=",1)[1]
          if buff!="" and buff!=" ":
            self.PreparationString="nTrain_Background="+buff+":"+self.PreparationString
        if "nTest_Signal" in line:
          buff=line.split("=",1)[1]
          if buff!="" and buff!=" ":
            self.PreparationString="nTest_Signal="+buff+":"+self.PreparationString
        if "nTest_Background" in line:
          buff=line.split("=",1)[1]
          if buff!="" and buff!=" ":
            self.PreparationString="nTest_Background="+buff+":"+self.PreparationString
        if "SignalWeightExpression" in line:
          self.SignalWeightExpression=line.split("=",1)[1]
        if "BackgroundWeightExpression" in line:
          self.BackgroundWeightExpression=line.split("=",1)[1]
        if "MethodType" in line:
          self.MethodType=line.split("=",1)[1]
        if "MethodParams" in line:
          self.MethodParams=line.split("=",1)[1]
        if "UseEvenOddSplitting" in line:
          self.UseEvenOddSplitting=line.split("=",1)[1]
        if "SourceBackgroundTree" in line:
          self.BackgroundTreeName=line.split("=",1)[1]
        if "SourceSignalTree" in line:
          self.SignalTreeName=line.split("=",1)[1]
        if "RepeatTrainingNTimes" in line:
          self.RepeatTrainingNTimes=int(line.split("=",1)[1])
        if "DrawNRandomAsStartingVars" in line:
          self.DrawNRandomAsStartingVars=int(line.split("=",1)[1])
        if "SaveTrainingsToTrees" in line:
          self.SaveTrainingsToTrees=line.split("=",1)[1]
        if "coord" in line:
          buff=line.split("=",1)[1]
          coord=json.loads(buff)
          print "setting up coordinate ",coord
          if coord not in self.Coordinates:
            self.Coordinates.append(coord)
            self.BestCoordinatesGlobal.append([coord[0],0.0])
      #set up the que system
      self.QueHelper=QueHelper(RunSystem)


    def SetupParticles(self):
      for i in range(self.nParticles):
        call(["rm","-r","-f","Particles/Particle"+str(i)])
        call(['cp','-r','InitData',"Particles/Particle"+str(i)])
        call(['mv',"Particles/Particle"+str(i)+"/PSO.sh","Particles/Particle"+str(i)+"/PSO"+str(i)+".sh" ])
      #print str(self.nParticles)+" Particles set up"
        
    def InitParticles(self):
      for part in range(self.nParticles):
        #get starting values for the particle
        #uniformly distributed in coord space
        initialCoords=[]
        for coord in self.Coordinates:
          if coord[4]=="int":
            initValue=int(self.rand.Uniform(coord[1],coord[2]))
            initVelocity=int(self.rand.Uniform(-(coord[2]-coord[1]),(coord[2]-coord[1])))
            #now bound the velocity by the maximum
            initVelocity=int(cmp(initVelocity,0)*min(abs(initVelocity),coord[3]))
          elif coord[4]=="float":
            initValue=float(self.rand.Uniform(coord[1],coord[2]))
            initVelocity=float(self.rand.Uniform(-(coord[2]-coord[1]),(coord[2]-coord[1])))
            #now bound the velocity by the maximum
            initVelocity=float(cmp(initVelocity,0.0)*min(abs(initVelocity),coord[3]))
          else:
            print "ERROR: coordinates have to be int or float"
            exit(1)
          initialCoords.append([coord[0],initValue,initVelocity]) 
        print "Particle", part, " has inital coords ", initialCoords
        particle=Particle(
                         self.Path+"Particles/Particle"+str(part)+"/",
                         part,
                         self.Verbose,
                         self.usedVariables,
                         self.unusedVariables,
                         self.vw, self.vp, self.vg,
                         self.Coordinates,
                         initialCoords,
                         self.FOM,
                         self.KSThreshold,
                         self.FactoryString,
                         self.PreparationString,
                         self.SignalWeightExpression,
                         self.BackgroundWeightExpression,
                         self.SignalTreeName,
                         self.BackgroundTreeName,
                         self.MethodType,
                         self.MethodParams,
                         self.QueHelper,
                         self.MaxVariablesInCombination,
                         self.ImprovementThreshold,
                         self.RepeatTrainingNTimes,
                         self.DrawNRandomAsStartingVars,
                         self.SaveTrainingsToTrees,
                         self.UseEvenOddSplitting)
        #particle.SetTestPoint(initTree,initShrinkage,initBagging,initCuts,2,1,0)
        self.Particles.append(particle)
        
    def RunPSO(self):
      print "\n-------------------------------------------------------------"
      print "Starting Optimization"
      print "doing ", self.NIterations, " Iterations\n" 
      startTime=0
      finishTime=0
      totalTime=0.0
      nIterations=self.NIterations
      for it in range(nIterations):
        startTime=timer.time()
        for particle in self.Particles:
          particle.StartEvaluation()
        running=True
        print "\nIteration ", it
        if it!=0:
          estTime=totalTime/it * (nIterations-it)/60.0/60.0
          print "optimization finished in ca ", estTime, " hours"
        print "Number of particles finished :"
        while running:
          nFinished=0
          timer.sleep(30)
          for particle in self.Particles:
            partRun = particle.CheckJobStatus()
            if partRun==False:
              nFinished+=1
          #print nFinished
          sys.stdout.write(str(nFinished)+" ")
          sys.stdout.flush()
          #print(str(nFinished)+" "),
          if nFinished==self.nParticles:
            running=False
        print " "
        for particle in self.Particles:
          fom, KS, methodString, currentcoords, usedVars, unusedVars = particle.GetResult()
          if self.Verbose:
            print "particle returned: "
            print fom, KS, methodString, currentcoords, usedVars, unusedVars
          if fom>=self.TenBestMVAs[0][0]:
            if fom==0.0:
              self.TenBestMVAs[0]=[fom, KS, methodString, usedVars, unusedVars,currentcoords]
              #print "starting fix done"
            else:
              self.TenBestMVAs[9]=[fom, KS, methodString, usedVars, unusedVars,currentcoords]
              self.TenBestMVAs=sorted(self.TenBestMVAs, key=lambda s:s[0], reverse=True)
            #print "first"
          elif fom>=self.TenBestMVAs[9][0]:
            self.TenBestMVAs[9]=[fom, KS, methodString, usedVars, unusedVars,currentcoords]
            self.TenBestMVAs=sorted(self.TenBestMVAs, key=lambda s:s[0], reverse=True)
            #print "second"
        self.BestFOMGlobal=self.TenBestMVAs[0][0]
        self.BestKSGlobal=self.TenBestMVAs[0][1]
        self.BestCoordinatesGlobal=self.TenBestMVAs[0][5]
        #print self.TenBestMVAs[0]
        
        for particle in self.Particles:
          particle.UpdateParticle(self.BestCoordinatesGlobal,it,self.BestFOMGlobal,self.BestKSGlobal)
        print "\n------------------------------------------------------------------------"
        print "Best Result after Iteration "+str(it)
        print self.TenBestMVAs[0][:5]
        self.SaveStatus("PSOResult.txt")
        finishTime=timer.time()
        totalTime+=(finishTime-startTime)
        
     
     
    def PrintResult(self):
      print "Ten Best MVAs"
      for i in range(10):
        print self.TenBestMVAs[i][:5]

    def SaveStatus(self, SaveFile):
      savefile=open(SaveFile,"w")
      savefile.write("nParticles "+str(self.nParticles)+"\n")
      savefile.write("wIneratia "+str(self.vw)+"\n")
      savefile.write("wMemory "+str(self.vp)+"\n")
      savefile.write("wSwarm "+str(self.vg)+"\n")
      savefile.write("path "+str(self.Path)+"\n")
      savefile.write("usedVariables "+str(self.usedVariables)+"\n")
      savefile.write("unusedVariables "+str(self.unusedVariables)+"\n")
      savefile.write("KSThreshold "+str(self.KSThreshold)+"\n")
      savefile.write("TenBestMVAs\n")
      for i in range(10):
        savefile.write(str(self.TenBestMVAs[i][:5])+"\n")
      savefile.close()
      
      #for part in self.Particles:
        #part.SaveParticleStatus()
      
      splitPath = self.Path.split("/")
      #print splitPath
      last = splitPath[len(splitPath)-2]
      CatDef = last.partition("_")[2]
      #print CatDef
      bestBDTFile=open("FinalMVAConfig_"+CatDef+".txt","w")
      bestBDTFile.write("FOM "+str(self.TenBestMVAs[0][0])+"\n")
      bestBDTFile.write("KS "+str(self.TenBestMVAs[0][1])+"\n")
      bestBDTFile.write("Method "+str(self.TenBestMVAs[0][2])+"\n")
      bestBDTFile.write("Variables "+str(self.TenBestMVAs[0][3])+"\n")
      bestBDTFile.write("Factory "+str(self.FactoryString)+"\n")
      bestBDTFile.write("Preparation "+str(self.PreparationString)+"\n")
      bestBDTFile.write("SignalWeight "+str(self.SignalWeightExpression)+"\n")
      bestBDTFile.write("Preparation "+str(self.BackgroundWeightExpression)+"\n")
      bestBDTFile.write(str(self.TenBestMVAs[0][:5])+"\n")

      bestBDTFile.close()

    
    def GetVariableNumbers(self):
      outfile=open(self.Path+"/VariableNumbers.txt","w")
      for var in self.usedVariables:
        VarCount=0
        for i in range(self.nParticles):
          file=open(self.Path+"Particles/Particle"+str(i)+"/ParticleRoute.txt","r")
          lines=list(file)
          for line in lines:
            #print line
            if "0.0 " not in line:
              #print line
              if var in line:
                #print line
                VarCount+=1
          file.close()
        print var, VarCount
        outfile.write(var+" "+str(VarCount)+"\n")
      for var in self.unusedVariables:
        VarCount=0
        for i in range(self.nParticles):
          file=open(self.Path+"Particles/Particle"+str(i)+"/ParticleRoute.txt","r")
          lines=list(file)
          for line in lines:
            if "0.0 " not in line:
              if var in line:
                VarCount+=1
          file.close()
        print var, VarCount
        outfile.write(var+" "+str(VarCount)+"\n")
      outfile.close()

    def testFunction(self):
      for part in self.Particles:
        part.WriteConfig()
        part.UpdateParticle([[u'NTrees', 1000], [u'Shrinkage', 0.02], [u'GradBaggingFraction', 0.2], [u'nCuts', 50]])
        part.StartEvaluation()
        part.CheckJobStatus()
        print self.BestCoordinatesGlobal
        bg=[[u'NTrees', 0.0], [u'Shrinkage', 0.0], [u'GradBaggingFraction', 0.0], [u'nCuts', 0.0]]

      print "did the tests"

    def CompileAndSetupClientExecutable(self):
      print "Freshly Compiling PSO/Particle.C" 
      call(["g++ -o PSO/Particle PSO/Particle.C `root-config --cflags --glibs` -lTMVA"],shell=True)
      print "Copying the freshly compiled Particle exec to InitialData"
      call(["cp","PSO/Particle","InitData/Particle"])
      print "done"











