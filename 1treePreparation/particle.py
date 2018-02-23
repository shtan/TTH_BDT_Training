import ROOT
import math
from array import array
from subprocess import call
import sys

class Particle:
    def __init__(self, Path,particleNumber,Verbose, usedVariables, unusedVariables, vw, vp, vg, coordinates, initialcoordinates, FOM, KSThreshold, FactoryString, PreparationString, SignalWeightExpression, BackgroundWeightExpression, SignalTreeName, BackgroundTreeName, MethodType, MethodParams, QueHelper, MaxVariablesInCombination, ImprovementThreshold, RepeatTrainingNTimes, DrawNRandomAsStartingVars,SaveTrainingsToTrees,UseEvenOddSplitting):

      self.particleNumber=particleNumber
      self.Iteration=0
      self.Path=Path
      self.Verbose=Verbose
      self.JobID=0
      self.isrunning=False
      self.rand=ROOT.TRandom3(int(self.particleNumber)) ## Use seed=0 to get non reproduceability
      
      self.initialVariables=usedVariables
      self.additionalVariables=unusedVariables
      self.LastUsedVariables=[]
      self.LastUnusedVariables=[]
      self.vw=vw
      self.vp=vp
      self.vg=vg
      self.Coordinates=coordinates
      self.BestCoordinates=[]
      self.BestCoordinatesGlobal=[]
      for coord in self.Coordinates:
        self.BestCoordinates.append([coord[0],0.0])
        self.BestCoordinatesGlobal.append([coord[0],0.0])
      self.currentCoordinates=initialcoordinates
      self.FOM=FOM
      self.KSThreshold=KSThreshold
      self.FactoryString=FactoryString
      self.PreparationString=PreparationString
      self.SignalWeightExpression=SignalWeightExpression
      self.BackgroundWeightExpression=BackgroundWeightExpression
      self.SignalTreeName=SignalTreeName
      self.BackgroundTreeName=BackgroundTreeName
      self.MethodType=MethodType
      self.MethodParams=MethodParams
      self.QueHelper=QueHelper
      self.MaxVariablesInCombination=MaxVariablesInCombination
      self.ImprovementThreshold=ImprovementThreshold
      self.RepeatTrainingNTimes=RepeatTrainingNTimes
      self.DrawNRandomAsStartingVars=DrawNRandomAsStartingVars
      if self.Verbose:
          print "-------------------------------------------"
          print "setting up particle ",self.particleNumber
      if self.DrawNRandomAsStartingVars>0:
        allVars=self.initialVariables+self.additionalVariables
        il=len(allVars)
        self.initialVariables=[]
        for i in range(self.DrawNRandomAsStartingVars):
          idx=int(self.rand.Uniform(0,len(allVars)))
          var=allVars.pop(idx)
          self.initialVariables.append(var)
        self.additionalVariables=allVars
        if self.Verbose:
          print "Drawing ", self.DrawNRandomAsStartingVars, " starting Variables"
          print "usedVars\n", self.initialVariables
          print "unusedVariables\n", self.additionalVariables
          print il, len(self.initialVariables), len(self.additionalVariables)
      self.SaveTrainingsToTrees=SaveTrainingsToTrees
      self.UseEvenOddSplitting=UseEvenOddSplitting
     
      self.AllVariablesAtStart=self.additionalVariables+self.initialVariables
      self.AllVariablesAfterIteration=self.AllVariablesAtStart

      self.BestFOM=0.0
      self.BestKS=0.0
      self.BestFOMGlobal=0.0
      self.BestKSGlobal=0.0

      #write the job and run files
      jobfile=open(self.Path+"PSO"+str(self.particleNumber)+".sh" ,"w")
      execlines=self.QueHelper.GetExecLines()
      for line in execlines:
        jobfile.write(line)
      jobfile.write("cd "+self.Path+"\n")
      jobfile.write("./Particle")
      jobfile.close()
      
      runfile=open(self.Path+"run.sh","w")
      runlines=self.QueHelper.GetRunLines()
      for line in runlines:
        line=line.replace("INSERTPATHHERE",self.Path)
        line=line.replace("INSERTEXECSCRIPTHERE","./Particles/Particle"+str(self.particleNumber)+"/PSO"+str(self.particleNumber)+".sh")
        runfile.write(line)
      runfile.close()
      
      self.WriteConfig()
      
    def WriteConfig(self):
      #write ConfigFile
      configfile=open(self.Path+"ParticleConfig.txt","w")
      configfile.write("particleNumber "+str(self.particleNumber)+"\n")
      configfile.write("Iteration "+str(self.Iteration)+"\n")
      configfile.write("FOM "+str(self.FOM)+"\n")
      configfile.write("SaveTrainingsToTrees "+str(self.SaveTrainingsToTrees)+"\n")
      configfile.write("KSThreshold "+str(self.KSThreshold)+"\n")
      configfile.write("FactoryString "+str(self.FactoryString)+"\n")
      configfile.write("PreparationString "+str(self.PreparationString)+"\n")
      configfile.write("SignalWeightExpression "+str(self.SignalWeightExpression)+"\n")
      configfile.write("BackgroundWeightExpression "+str(self.BackgroundWeightExpression)+"\n")
      configfile.write("SignalTreeName "+str(self.SignalTreeName)+"\n")
      configfile.write("BackgroundTreeName "+str(self.BackgroundTreeName)+"\n")
      configfile.write("UseEvenOddSplitting "+str(self.UseEvenOddSplitting)+"\n")
      configfile.write("MaxVariablesInCombination "+str(self.MaxVariablesInCombination)+"\n")
      configfile.write("ImprovementThreshold "+str(self.ImprovementThreshold)+"\n")
      configfile.write("RepeatTrainingNTimes "+str(self.RepeatTrainingNTimes)+"\n")
      configfile.write("MethodType "+str(self.MethodType)+"\n")
      methodString=self.MethodParams
      #print methodString
      for coord in self.currentCoordinates:
        configfile.write("coord "+coord[0]+" "+str(coord[1])+"\n")
        if coord[0] in methodString:
          splitMethods=methodString.split(":")
          for i,par in enumerate(splitMethods):
            if par.split("=",1)[0]==coord[0]:
              val=par.split("=",1)[1]
              splitMethods[i]=par.replace(val,str(coord[1]))
              break
          newMethods=":"
          methodString=newMethods.join(splitMethods)
      self.MethodParams=methodString
      configfile.write("MethodParameters "+str(self.MethodParams)+"\n")

      configfile.write("--InitialVariables--"+"\n")
      for var in self.initialVariables:
        configfile.write(var+"\n")
      configfile.write("--EndInitVars--\n")
      configfile.write("--additionalVariables--\n")
      for var in self.additionalVariables:
        configfile.write(var+"\n")
      configfile.write("--EndAddVars--\n")
      configfile.close()
    
    def StartEvaluation(self):
      self.JobID=self.QueHelper.StartJob("./Particles/Particle"+str(self.particleNumber)+"/run.sh")
      #print self.JobID
    
    def CheckJobStatus(self):
      self.isrunning=self.QueHelper.GetIsJobRunning(self.JobID)
      return self.isrunning
            
    def UpdateParticle(self, BestCoordsGlobal,Iteration,bestFOMGlobal, bestKSGlobal):
      self.Iteration=Iteration
      self.BestCoordinatesGlobal=BestCoordsGlobal
      self.BestFOMGlobal=bestFOMGlobal
      self.BestKSGlobal=bestKSGlobal
      
      if self.Verbose:
        print "\nUpdating particle ",self.particleNumber
        print "current ", self.currentCoordinates
        print "best global ", self.BestCoordinatesGlobal
        print "best particle ", self.BestCoordinates
      newCoords=[]
      for coord in self.Coordinates:
        curVel=0
        newVel=0
        cc="bla"
        newcoord=""
        bcg=""
        bcp=""
        for c in self.BestCoordinatesGlobal:
          if coord[0]==c[0]:
            bcg=c[1]
            break
        for c in self.BestCoordinates:
          if coord[0]==c[0]:
            bcp=c[1]
            break
        for c in self.currentCoordinates:
          if coord[0]==c[0]:
            cc=c[1]
            curVel=c[2]
            break
        rp=self.rand.Rndm()
        rg=self.rand.Rndm()
        newVel=self.vw*curVel + self.vp*rp*(bcp-cc)+self.vg*rg*(bcg-cc)
        newVel=cmp(newVel,0)*min(abs(newVel),coord[3])
        if coord[4]=="int":
          newVel=int(newVel)
        elif coord[4]=="float":
          newVel=float(newVel)
        newcoord=cc+newVel
        newcoord=abs(cmp(newcoord,0)*min(abs(newcoord),coord[2]))
        newcoord=abs(cmp(newcoord,0)*max(abs(newcoord),coord[1]))
        if self.Verbose:
          print "\nOld Coordinate ", coord[0],cc,curVel
          print "best global ", bcg
          print "best for this particle ", bcp
        if self.Verbose:
          print "New Coordinate ", newcoord, newVel
        newCoords.append([coord[0],newcoord,newVel])
       
      self.currentCoordinates=newCoords
      #print self.currentCoordinates
      self.WriteConfig()

    def GetResult(self):
      resultfile=open(self.Path+"ParticleResult.txt","r")
      lines=list(resultfile)
      #print lines
      fom=0.0
      ks=0.0
      self.LastUsedVariables=self.initialVariables
      self.LastUnusedVariables=self.additionalVariables
      self.initialVariables=[]
      self.additionalVariables=[]
      #print lines
      for line in lines:
        if "BestFOM" in line:
          fom=float(line.split(" ",1)[1])
        if "KSScore" in line:
          ks=float(line.split(" ",1)[1])
        if "MethodString" in line:
          self.MethodParams=line.split(" ",1)[1].strip()
          #print self.MethodParams
        if "UsedVar" in line:
          self.initialVariables.append(line.split(" ",1)[1].strip())
        if "UnusedVars" in line:
          self.additionalVariables.append(line.split(" ",1)[1].strip())
      resultfile.close()

      #self.AllVariablesAfterIteration=self.initialVariables+self.additionalVariables
      self.additionalVariables=[]
      for vv in self.AllVariablesAtStart:
        if vv not in self.initialVariables:
          self.additionalVariables.append(vv)
      
      if ks<self.KSThreshold:
        fom=0.0
        ks=0.0
        #print ROC
      else:
        if fom>=self.BestFOM:
          self.BestFOM=fom
          self.BestKS=ks
          self.BestCoordinates=[]
          for coord in self.currentCoordinates:
            self.BestCoordinates.append([coord[0],coord[1]])
      if self.Verbose:
        print "particle ", self.particleNumber
        print self.BestCoordinates
        print self.BestFOM
      
      RouteFile=open(self.Path+"ParticleRoute.txt","a")
      Route=str(fom).replace("\n","")+" "+str(ks).replace("\n","")+" "
      for ccc in self.currentCoordinates:
        Route+=str(ccc[1])+" "
      Route+=str(self.additionalVariables)+"\n"
      RouteFile.write(Route)
      RouteFile.write("--Next--\n")
      RouteFile.close()
      
      return fom, ks, self.MethodParams, self.currentCoordinates, self.initialVariables, self.additionalVariables
      
    #def SaveParticleStatus(self):
      #PartSavefile=open(self.Path+"ParticleStatus.txt","w")
      ##PartSavefile.write(str(self.Path)+"\n")
      #PartSavefile.write(str(self.KSThreshold)+"\n")
      #PartSavefile.write(str(self.usedVariables)+"\n")
      #PartSavefile.write(str(self.unusedVariables)+"\n")
      #PartSavefile.write(str(self.particleNumber)+"\n")
      #PartSavefile.write(str(self.BestROC)+"\n")
      #PartSavefile.write(str(self.BestKS)+"\n")
      #PartSavefile.write(str(self.BestNTrees)+"\n")
      #PartSavefile.write(str(self.BestShrinkage)+"\n")
      #PartSavefile.write(str(self.BestBagging)+"\n")
      #PartSavefile.write(str(self.BestCuts)+"\n")
      #PartSavefile.write(str(self.BestDepth)+"\n")
      #PartSavefile.write(str(self.VelTree)+"\n")
      #PartSavefile.write(str(self.VelShrinkage)+"\n")
      #PartSavefile.write(str(self.VelBagging)+"\n")
      #PartSavefile.write(str(self.VelCuts)+"\n")
      #PartSavefile.write(str(self.VelDepth)+"\n")
      #PartSavefile.write(str(self.NTrees)+"\n")
      #PartSavefile.write(str(self.Shrinkage)+"\n")
      #PartSavefile.write(str(self.Bagging)+"\n")
      #PartSavefile.write(str(self.Cuts)+"\n")
      #PartSavefile.write(str(self.Depth)+"\n")
      #PartSavefile.close()
      















