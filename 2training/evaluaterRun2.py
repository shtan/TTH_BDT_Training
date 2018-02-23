import ROOT
from array import array
from subprocess import call

class Systematic:
    def __init__(self,name,nameup="",samplesuffixup="", weightup="",namedown="",samplesuffixdown="", weightdown=""):
        self.name=name
        self.name_up=nameup
        self.name_down=namedown
        self.samplesuffix_up=samplesuffixup
        self.samplesuffix_down=samplesuffixdown
        self.weight_up=weightup
        self.weight_down=weightdown

class Sample:
    def __init__(self,name,path,constraint,scale=1.):
        self.name=name
        self.path=path
        self.scale=scale
        self.constraint=constraint
      

class Evaluater:
    def __init__(self,weightfile ,variables, samples,data,systematics):
        self.weightfile=weightfile
        self.variables=variables
        self.samples=samples
        self.data=data
        self.systematics=systematics
        self.init_reader()


    def init_reader(self):
        self.reader = ROOT.TMVA.Reader()
        self.arraylist=[]
        for var in self.variables:
            self.arraylist.append( array('f',[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]) )
            self.reader.AddVariable(str(var),self.arraylist[-1])
        self.reader.BookMVA("BDTG",self.weightfile)
        self.reader.SetVerbose(True)

    def fillHisto(self,outfile,histoname,path,weightname="",scale=1.,nBins=10, minX=-1.0, maxX=1.0):
        nDiLepton=0
        nless=0
        n4=0
        n5=0
        n6=0
        print path
        histo = ROOT.TH1F(histoname,histoname,nBins,minX,maxX)
        f = ROOT.TFile( path )
        tree     = f.Get("MVATree")
        # init variables
        i=0                
        for var in self.variables:
           # print var, type(var)
            if "[" in var:
              var=var.split("[",1)[0]
              #print var
            tree.SetBranchAddress( var, self.arraylist[i] )
            i+=1
        # init weight
        weight=array('f',[1.])
        weight_xs=array('f',[1.])
        njets=array('i',[1])
        tree.SetBranchAddress( "Weight", weight )
        tree.SetBranchAddress( "Weight_XS", weight_xs )
        tree.SetBranchAddress("N_Jets",njets)
        csv0=array('f',[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        tree.SetBranchAddress("CSV",csv0)
        isttH=array('i',[0])
        tree.SetBranchAddress("Istth",isttH)
        isttbar=array('i',[0])
        tree.SetBranchAddress("Isttbar",isttbar)

        sysweight=array('f',[1.])
        if weightname!="" :
            tree.SetBranchAddress( weightname, sysweight )
        
        # event loop
        for ievt in range(tree.GetEntries()):
            tree.GetEntry(ievt)
            if abs(csv0[0])>1.0:
              #print csv0[0]
              continue
            output = self.reader.EvaluateMVA("BDTG")
            if output<=-2.0:
              print "WARNING WARNING", output
              jj=0
              for v in self.variables:
                print v, self.arraylist[jj][0]
                jj+=1
              continue
            scale_1=scale
            sysweight_1=sysweight[0]
            #print njets[0]
            if "ttbar_0p" in histoname:
              n4+=1
              if njets[0]!=4:
                n4-=1
                sysweight_1=1.0
            if "ttbar_1p" in histoname:
              n5+=1
              if njets[0]!=5:
                n5-=1
                sysweight_1=1.0
            if "ttbar_2p" in histoname:
              n6+=1
              if njets[0]<6:
                n6-=1
                sysweight_1=1.0
            if "ttbar_less" in histoname:
              nless+=1
              if njets[0]>3:
                nless-=1
                sysweight_1=1.0
            
            datattbarweight=1.0
            if "MCData" in path:
              if isttH[0]==1 or isttbar[0]==1:
                datattbarweight=2.0
            histo.Fill(output,weight[0]*sysweight_1*scale_1*datattbarweight)
        histo.SetBinContent(0,histo.GetBinContent(0)+histo.GetBinContent(1))
        histo.SetBinContent(nBins,histo.GetBinContent(nBins)+histo.GetBinContent(nBins+1))
        outfile.cd()
        histo.Write()
        #print 'filled '+histoname+', integral: '+str(histo.Integral())
        #print nDiLepton
        #print n4, n5, n6, nless
        return histo.Integral()

    def doBinStatistics(self, outfile, path,category,datacard,nBins=10,minX=-1.0,maxX=1.0):
      bkgSum_histo=None
      
      data_hist=ROOT.TH1F("data_hist","data_hist",nBins,minX,maxX)
      data_hist.Sumw2()
      f = ROOT.TFile(self.data.path)
      tree     = f.Get("MVATree")
      
      i=0                
      for var in self.variables:
          if "[" in var:
              var=var.split("[",1)[0]
              #print var
          tree.SetBranchAddress( var, self.arraylist[i] )
          i+=1
      # init variables
      #BDToutput = array('f', [0])
      #tree.SetBranchAddress( "_output", BDToutput )
      # init weight
      weight=array('f',[1.])
      weight_xs=array('f',[1.])
      tree.SetBranchAddress( "Weight_XS", weight_xs )
      tree.SetBranchAddress( "Weight", weight )
      csv0=array('f',[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
      isttH=array('i',[0])
      tree.SetBranchAddress("Istth",isttH)
      isttbar=array('i',[0])
      tree.SetBranchAddress("Isttbar",isttbar)
      tree.SetBranchAddress("CSV",csv0)
      for ievt in range(tree.GetEntries()):
            tree.GetEntry(ievt)
            output = self.reader.EvaluateMVA("BDTG")
            scale_1=self.data.scale
            datattbarscale=1.0
            if isttH[0]==1 or isttbar[0]==1:
              datattbarscale=2.0
            data_hist.Fill(output,weight[0]*scale_1*datattbarscale)
      f.Close()
      
      sig_hist=ROOT.TH1F("sig_hist","sig_hist",nBins,minX,maxX)
      sig_hist.Sumw2()
      f = ROOT.TFile(self.samples[0].path)
      tree     = f.Get("MVATree")
      # init variables
      #BDToutput = array('f', [0])
      #tree.SetBranchAddress( "FinalBDT", BDToutput )
      # init weight
      i=0                
      for var in self.variables:
          if "[" in var:
              var=var.split("[",1)[0]
              #print var
          tree.SetBranchAddress( var, self.arraylist[i] )
          i+=1
      weight=array('f',[1.])
      tree.SetBranchAddress( "Weight", weight )
      csv0=array('f',[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
      tree.SetBranchAddress("CSV",csv0)
      for ievt in range(tree.GetEntries()):
            tree.GetEntry(ievt)
            output = self.reader.EvaluateMVA("BDTG")
            sig_hist.Fill(output,weight[0]*self.samples[0].scale)
      f.Close()
      
      bkg_histos=[]
      i=0
      for sample in self.samples:
        if sample.name=="tth" or sample.name=="ttH":
          continue
        bkg_histos.append(ROOT.TH1F(sample.name,sample.name,nBins,minX,maxX))
        bkg_histos[i].Sumw2()
        f = ROOT.TFile(sample.path)
        tree     = f.Get("MVATree")
      # init variables
        j=0                
        for var in self.variables:
            if "[" in var:
              var=var.split("[",1)[0]
              #print var
            tree.SetBranchAddress( var, self.arraylist[j] )
            j+=1
        #BDToutput = array('f', [0])
        #tree.SetBranchAddress( "FinalBDT", BDToutput )
      # init weight
        weight=array('f',[1.])
        weight_xs=array('f',[1.])
        tree.SetBranchAddress( "Weight_XS", weight_xs )
        tree.SetBranchAddress( "Weight", weight )
        csv0=array('f',[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        tree.SetBranchAddress("CSV",csv0)
        for ievt in range(tree.GetEntries()):
            tree.GetEntry(ievt)
            output = self.reader.EvaluateMVA("BDTG")
            scale_1=sample.scale
            bkg_histos[i].Fill(output,weight[0]*scale_1)
        f.Close()
        #print len(bkg_histos), bkg_histos[i].Integral() 
      #do background sum
        if bkgSum_histo:
          bkgSum_histo.Add(bkg_histos[i])
        else:
          bkgSum_histo = bkg_histos[i].Clone()
        i+=1
        #print bkgSum_histo.Integral()
      
      # done reading the histos now check for small bins
      i=0
      for sample in self.samples:
        
        if sample.name=="tth" or sample.name=="ttH":
          continue
        hist=bkg_histos[i].Clone()
        #print i
        for b in range(1,nBins+1):
          data = data_hist.GetBinContent(b)
          data_err = data_hist.GetBinError(b)
          sig = sig_hist.GetBinContent(b)
          sig_err = sig_hist.GetBinError(b)
          bkg = bkgSum_histo.GetBinContent(b)
          bkg_err = bkgSum_histo.GetBinError(b)
          val = hist.GetBinContent(b)
          val_err = hist.GetBinError(b)
          
          other_frac = ROOT.TMath.Sqrt(bkg_err**2 - val_err**2)
          #print sample.name, category, bkg, bkg_err, sig, sig_err, data, data_err
          #print sample.name, category, val, val_err, bkg_err, data_err/5., other_frac/bkg_err, sig/bkg

          #Changed from data_err/3 -> data_err/5 and sig/bkg < 0.02 -> 0.01 - KPL
          if val < .01 or bkg_err < data_err / 5. or other_frac / bkg_err > .95 or sig / bkg < .01:
            continue
          hist_up=hist.Clone("output_Stat"+category+"_"+sample.name+"_AnnBin_"+str(b)+"Up_"+sample.name)
          hist_down=hist.Clone("output_Stat"+category+"_"+sample.name+"_AnnBin_"+str(b)+"Down_"+sample.name)
          hist_down.GetSumw2().Set(0)
          hist_up.GetSumw2().Set(0)
          newValUp=val + val_err
          newValDown=val - val_err
          if newValDown<=0:
            newValDown=0.00001
            #print "!! setting statdown bin to ", newValDown
          hist_up.SetBinContent(b, newValUp)
          hist_down.SetBinContent(b, newValDown)                   
             
          outfile.cd()
          hist_up.Write()
          hist_down.Write()
          #print "wrote ", "output_Stat"+category+"_"+sample.name+"_AnnBin_"+str(b)
          datacard.write("Stat"+category+"_"+sample.name+"_AnnBin_"+str(b)+'\t')
          datacard.write('shape\t')
          for s in self.samples:
              if s.name==sample.name:
                 datacard.write('1')
                 datacard.write('\t')
              else:
                datacard.write('-')
                datacard.write('\t')
          datacard.write('\n')
        i+=1
     
    def fillTree(self,oldpath,newpath, bdt=""):
        print oldpath
        oldfile = ROOT.TFile( oldpath )
        oldtree = oldfile.Get( "MVATree" )
        nentries =oldtree.GetEntries()
        newfile = ROOT.TFile(newpath ,"recreate" )
        newtree = oldtree.CloneTree(0)
        i=0                
        for var in self.variables:
            if "[" in var:
              var=var.split("[",1)[0]
              #print var
            oldtree.SetBranchAddress( var, self.arraylist[i] )
            i+=1
        # init bdtoutput
        output=array('f',[-2.])
        
        csv0=array('f',[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        oldtree.SetBranchAddress("CSV",csv0)
        
        newtree.Branch( bdt+"_KIT_output",output,bdt+"_KIT_output/F"  )
        weight_xs=array('f',[1.])
        oldtree.SetBranchAddress( "Weight_XS", weight_xs )


        # event loop
        for ievt in range(nentries):
            oldtree.GetEntry(ievt)
            if abs(csv0[0])>1.0:
              print "skipping event with csv>>1"
              continue
            output[0] = self.reader.EvaluateMVA("BDTG")
            if output[0]<=-2.0:
              print "WARNING WARNING", output[0] 
              continue
            newtree.Fill()
        newtree.AutoSave()
        oldfile.Close()
        newfile.Close()
        
    def writeline(self,datacard):
        datacard.write('----------------------------------------------------------------------------------------------------\n')

    def writeheader(self,datacard,category,Analysis,observed):
        datacard.write('imax 1 number of channels\n')
        datacard.write('jmax * number of backgrounds\n')
        datacard.write('kmax * number of nuisance parameters\n')
        self.writeline(datacard)
        datacard.write('bin\tC'+category+'\n')
        datacard.write('observation\t'+str(observed)+'\n')
        datacard.write('shapes\t*\tC'+category+'\thistos_'+category+'_'+Analysis+'.root\toutput_nominal_$PROCESS\toutput_$SYSTEMATIC_$PROCESS\toutput_$SYSTEMATIC_$PROCESS\n')
        datacard.write('shapes\tdata_obs\tC'+category+'\thistos_'+category+'_'+Analysis+'.root\toutput_data\n')
        self.writeline(datacard)
        
        
    def writeprocesses(self,datacard,category):
        datacard.write('bin\t')
        for sample in self.samples:
            datacard.write('C'+category)
            datacard.write('\t')
        datacard.write('\n')

        datacard.write('process\t')
        for sample in self.samples:
            datacard.write(sample.name)
            datacard.write('\t')
        datacard.write('\n')

        datacard.write('process\t')
        for i in range(len(self.samples)):
            datacard.write(str(i))
            datacard.write('\t')
        datacard.write('\n')

    def writerate(self,datacard,rate):
        datacard.write('rate\t')
        for r in rate:
            datacard.write("%.4f" % r)
            datacard.write('\t')
        datacard.write('\n')

    def writeratesys(self,datacard,name,type,size):
        datacard.write(name+'\t')
        datacard.write(type+'\t')
        for sample in self.samples:
            if sample.name in size:
                datacard.write(str(size[sample.name]))
            else:
                datacard.write('-')
            datacard.write('\t')
        datacard.write('\n')

    def writeshapesys(self,datacard,systematics):
        for systematic in systematics:
            if "Q2Scale" in systematic.name:
              continue
            datacard.write(systematic.name+'\t')
            datacard.write('shape\t')
            for sample in self.samples:
                datacard.write('1')
                datacard.write('\t')
            datacard.write('\n')
        
    def writelnNsys(self,datacard,cat=""):
        # tth ttl ttb ttbb tt2b ttcc singlet diboson ttW ttZ ZJets
        datacard.write('lumi\tlnN\t1.025\t1.025\t1.025\t1.025\t1.025\t1.025\t1.025\t1.025\t1.025\t1.025\n')
        #datacard.write('CMS_tth_eff_lep\tlnN\t1.014\t1.014\t1.014\t1.014\t1.014\t1.014\t1.014\t1.014\t1.014\n')
        #datacard.write('QCDscale_V\tlnN\t-\t-\t-\t-\t-\t-\t1.013\t1.012\t-\n')
        #datacard.write('QCDscale_VV\tlnN\t-\t-\t-\t-\t-\t-\t-\t-\t1.036\n')
        
        
        #datacard.write('Q2Scale_ttbar_bb\tshape\t-\t1\t-\t-\t-\t-\t-\t-\t-\n')
        #datacard.write('Q2Scale_ttbar_b\tshape\t-\t-\t1\t-\t-\t-\t-\t-\t-\n')
        #datacard.write('Q2Scale_ttbar_cc\tshape\t-\t-\t-\t1\t-\t-\t-\t-\t-\n')
        #if cat=="44" or cat=="43":
           #datacard.write('Q2Scale_ttbar_0p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_1p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_2p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_V\tlnN\t-\t-\t-\t-\t-\t-\t1.477\t1.477\t-\n')
           #datacard.write('Q2Scale_ttbar_less\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')


        #if cat=="54" or cat=="53":
           #datacard.write('Q2Scale_ttbar_0p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_1p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_2p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_V\tlnN\t-\t-\t-\t-\t-\t-\t1.618\t1.618\t-\n')
           #datacard.write('Q2Scale_ttbar_less\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')

        #if cat=="64" or cat=="63" or cat=="62":
           #datacard.write('Q2Scale_ttbar_0p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_1p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_2p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_V\tlnN\t-\t-\t-\t-\t-\t-\t1.766\t1.766\t-\n')
           #datacard.write('Q2Scale_ttbar_less\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')

        #if cat=="boosted" or cat=="DB" or cat=="SBT" or cat=="SBH":
           #datacard.write('Q2Scale_ttbar_0p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_1p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_2p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_less\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_V\tlnN\t-\t-\t-\t-\t-\t-\t1.766\t1.766\t-\n')

        #datacard.write('QCDscale_tth\tlnN\t1.067\t-\t-\t-\t-\t-\t-\t-\t-\n')
        datacard.write('QCDscale_ttbar\tlnN\t-\t1.036\t1.036\t1.036\t1.036\t1.036\t-\t-\t-\t-\n')
        datacard.write('pdf_gg\tlnN\t1.092\t1.043\t1.043\t1.043\t1.043\t1.043\t-\t-\t-\t1.025\n')
        datacard.write('pdf_qqbar\tlnN\t-\t-\t-\t-\t-\t-\t-\t-\t1.017\t-\n')
        datacard.write('pdf_qg\tlnN\t-\t-\t-\t-\t-\t-\t1.048\t-\t-\t-\n')

        #datacard.write('CMS_res_j\tlnN\t1.015\t1.015\t1.015\t1.015\t1.015\t1.015\n')
        #datacard.write('CMS_tth_pu\tlnN\t1.01\t1.01\t1.01\t1.01\t1.01\t1.01\n')


    def run(self,category="", bdtversion=""):
        nBins, minX, maxX = self.GetHistoConfig(category)

        nominal_integrals=[]
        outfile=ROOT.TFile( "histos_"+category+"_"+bdtversion+".root" ,"recreate")
        observed=self.fillHisto(outfile,"output_data",self.data.path,"",self.data.scale,nBins, minX, maxX)
        for sample in self.samples:
            h="output_nominal_"+sample.name
            p=sample.path
            w=""
            s=sample.scale
            #print s
            integral=self.fillHisto(outfile,h,p,w,s,nBins, minX, maxX)
            self.fillTree(p,sample.path.replace(".root","_output.root"))
            self.fillTree(sample.path.replace("nominal","JESUP"),sample.path.replace("_nominal.root","_JESUP_output.root"))
            self.fillTree(sample.path.replace("nominal","JESDOWN"),sample.path.replace("_nominal.root","_JESDOWN_output.root"))
            self.fillTree(sample.path.replace("nominal","JERUP"),sample.path.replace("_nominal.root","_JERUP_output.root"))
            self.fillTree(sample.path.replace("nominal","JERDOWN"),sample.path.replace("_nominal.root","_JERDOWN_output.root"))

            nominal_integrals.append(integral)

            for sys in self.systematics:
                print sys.name
                if sys.name=="Q2Scale_ttbar_bb" and sample.name!="ttbar_bb":
                  continue
                if sys.name=="Q2Scale_ttbar_b" and sample.name!="ttbar_b":
                  continue
                if sys.name=="Q2Scale_ttbar_cc" and sample.name!="ttbar_cc":
                  continue
                if (sys.name=="Q2Scale_ttbar_0p" or sys.name=="Q2Scale_ttbar_1p" or sys.name=="Q2Scale_ttbar_2p" or sys.name=="Q2Scale_ttbar_less") and sample.name!="ttbar_light":
                  continue
                
                if sys.name_up!="":
                    h="output_"+sys.name_up+"_"+sample.name
                    if sys.samplesuffix_up!="":
                      print "replacing"
                      print "bla", p
                      p=sample.path.replace("_nominal.root",sys.samplesuffix_up+".root")
                    else:
                      p=sample.path.replace(".root",sys.samplesuffix_up+".root")
                    w=sys.weight_up
                    s=sample.scale
                    integral=self.fillHisto(outfile,h,p,w,s,nBins, minX, maxX)

                if sys.name_down!="":
                    h="output_"+sys.name_down+"_"+sample.name
                    if sys.samplesuffix_down!="":
                      p=sample.path.replace("_nominal.root",sys.samplesuffix_down+".root")
                    else:
                      p=sample.path.replace(".root",sys.samplesuffix_down+".root")
                    w=sys.weight_down
                    s=sample.scale
                    self.fillHisto(outfile,h,p,w,s,nBins, minX, maxX)
                    
        datacard=open('datacard.txt','w')
        self.writeheader(datacard,category,bdtversion,"%.4f" %observed)
        self.writeprocesses(datacard,category)            
        self.writerate(datacard,nominal_integrals)
        self.writeline(datacard)
        #self.writeshapes
        for sample in self.samples:
            if sample.constraint > 0:
                self.writeratesys(datacard,"QCDscale_"+sample.name,"lnN",{sample.name:1.+sample.constraint})
        self.writelnNsys(datacard,category)
        self.writeshapesys(datacard,self.systematics)
        self.doBinStatistics(outfile, p,category,datacard ,nBins, minX, maxX)
        datacard.close()
        outfile.Close()
        call(['cp',"histos_"+category+"_"+bdtversion+".root","output/histos_"+category+"_"+bdtversion+".root"])
        datacardname="output/datacard_"+category+"_"+bdtversion+".txt"
        call(['cp','datacard.txt',datacardname])
#        call(['combine','-M','Asymptotic','datacard.txt','-t','-1'])
        file = open("output/Limit_"+category+"_"+bdtversion+".txt","w")
        #call(['combine','-v','0','-M', 'ProfileLikelihood' ,'datacard.txt', '-t' ,'10'],stdout=file)
        #call(['combine','-v','0','-M', 'Asymptotic','--minosAlgo','stepping' ,'datacard.txt', '--run=blind'],stdout=file)
        file.close()
        
        
        #call(['combine','-M', 'MaxLikelihoodFit' ,'datacard.txt'])

    def WriteBDTVars(self,inputsuffix, outputsuffix, bdt=""):
        for sample in self.samples:
            p=sample.path
            self.fillTree(sample.path.replace(".root",inputsuffix+".root"),sample.path.replace(".root",outputsuffix+".root"),bdt)
            
    def WriteEvalBDTVars(self,inputsuffix, outputsuffix,bdt=""):
        for sample in self.samples:
            p=sample.path
            self.fillTree(p,sample.path.replace(".root",outputsuffix+".root"),bdt)
            self.fillTree(sample.path.replace(".root","_JESUP.root"),sample.path.replace(".root",outputsuffix+"_JESUP.root"),bdt)
            self.fillTree(sample.path.replace(".root","_JESDOWN.root"),sample.path.replace(".root",outputsuffix+"_JESDOWN.root"),bdt)
	    self.fillTree(sample.path.replace(".root","_JERUP.root"),sample.path.replace(".root",outputsuffix+"_JERUP.root"),bdt)
            self.fillTree(sample.path.replace(".root","_JERDOWN.root"),sample.path.replace(".root",outputsuffix+"_JERDOWN.root"),bdt)
##old version of this function
    def GetHistoConfig(self, category):
      minX=-0.0
      maxX=0.0
      nBins=10
      for sample in self.samples:
        print sample.name
        if sample.name=="tth":
          print "tth continuing"
          continue
        f = ROOT.TFile( sample.path )
        tree     = f.Get("MVATree")
        bufferfile=ROOT.TFile("bufferfile.root","recreate")
        newtree = ROOT.TTree("bufferTree","bufferTree")
        i=0                
        for var in self.variables:
            if "[" in var:
              var=var.split("[",1)[0]
              #print var
            tree.SetBranchAddress( var, self.arraylist[i] )
            i+=1
        # init bdtoutput
        output=array('f',[-2.])
        newtree.Branch( "buffer",output,"buffer/F"  )
        csv0=array('f',[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        tree.SetBranchAddress("CSV",csv0)
       
        # event loop
        for ievt in range(tree.GetEntries()):
            tree.GetEntry(ievt)
            if abs(csv0[0])>1.0:
              continue
            output[0] = self.reader.EvaluateMVA("BDTG")
            if output[0]<=-2.0:
              print "WARNING WARNING", output[0] 
              continue
            newtree.Fill()
        
        
        x1=newtree.GetMinimum("buffer")
        x2=newtree.GetMaximum("buffer")
        print x1, x2
        f.Close()
        bufferfile.Close()
        if x1<=minX:
          minX=x1
        if x2>=maxX:
          maxX=x2
      
      if minX<-1.0:
         minX=-1.0
      if maxX>1.0:
         maxX=1.0
        
      if category=="43":
        nBins=20
      elif category=="44":
        nBins=10
      elif category=="53":
        nBins=20
      elif category=="54":
        nBins=10
      elif category=="62":
        nBins=20
      elif category=="63":
        nBins=20
      elif category=="64":
        nBins=10
      elif category=="DB":
        nBins=10
      else:
        nBins = 10
      print "HistoConfig ", nBins, minX-.01, maxX+.01
      return nBins, minX-.01, maxX+.01 
      
##new version for testing 
## very WIP !!!!
    #def GetHistoConfig(self, category):
      #minX=-0.0
      #maxX=0.0
      #nBins=10
      #for sample in self.samples:
        #print sample.name
        #f = ROOT.TFile( sample.path )
        #tree     = f.Get("MVATree")
        #bufferfile=ROOT.TFile("bufferfile.root","recreate")
        #newtree = ROOT.TTree("bufferTree","bufferTree")
        #i=0                
        #for var in self.variables:
            #tree.SetBranchAddress( var, self.arraylist[i] )
            #i+=1
        ## init bdtoutput
        #output=array('f',[-2.])
        #newtree.Branch( "buffer",output,"buffer/F"  )
        #csv0=array('f',[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        #tree.SetBranchAddress("CSV",csv0)
       
        ## event loop
        #for ievt in range(tree.GetEntries()):
            #tree.GetEntry(ievt)
            #if abs(csv0[0])>1.0:
              #continue
            #output[0] = self.reader.EvaluateMVA("BDTG")
            #if output[0]<=-2.0:
              #print "WARNING WARNING", output[0] 
              #continue
            #newtree.Fill()
        
        #x1=newtree.GetMinimum("buffer")
        #x2=newtree.GetMaximum("buffer")
        #print x1, x2
        #f.Close()
        #bufferfile.Close()
        #if x1<=minX:
          #minX=x1
        #if x2>=maxX:
          #maxX=x2
      
      #if minX<-1.0:
         #minX=-1.0
      #if maxX>1.0:
        #maxX=1.0
        
      #if category=="43":
        #nBins=20
      #elif category=="44":
        #nBins=10
      #elif category=="53":
        #nBins=20
      #elif category=="54":
        #nBins=10
      #elif category=="62":
        #nBins=20
      #elif category=="63":
        #nBins=20
      #elif category=="64":
        #nBins=10
      #else:
        #nBins = 10
      
      #loopcount=0
      ## test the binning
      #print "checking for empty background bins"
      #maxNbins=0
      #signalSampleNames=["tth","ttH","tthbb","ttHbb"]
            
      #for sample in self.samples:
        #print sample.name
        #if sample.name in signalSampleNames:
          #print "signal sample detected"
          #continue
        
        #f = ROOT.TFile( sample.path )
        #tree     = f.Get("MVATree")
        #bufferfile=ROOT.TFile("bufferfile.root","recreate")
        #newtree = ROOT.TTree("bufferTree","bufferTree")
        #i=0                
        #for var in self.variables:
            #tree.SetBranchAddress( var, self.arraylist[i] )
            #i+=1
        ## init bdtoutput
        #output=array('f',[-2.])
        #newtree.Branch( "buffer",output,"buffer/F"  )
        #csv0=array('f',[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        #tree.SetBranchAddress("CSV",csv0)
       
        ## event loop
        #for ievt in range(tree.GetEntries()):
            #tree.GetEntry(ievt)
            #if abs(csv0[0])>1.0:
              #continue
            #output[0] = self.reader.EvaluateMVA("BDTG")
            #if output[0]<=-2.0:
              #print "WARNING WARNING", output[0] 
              #continue
            #newtree.Fill()
        
        #foundBestBinning=False
        #currentNbins=nBins
        #bestNbins=999
        #while foundBestBinning==False:
          #loopcount+=1
          #print "testing nBins= ", currentNbins
          #BintestH=ROOT.TH1D("BintestH"+str(loopcount),"BintestH+str(loopcount)",currentNbins,minX-.01, maxX+.01)
          #newtree.Draw("buffer>>BintestH"+str(loopcount))
          #hasEmptyBin=False
          #for b in range(currentNbins):
            #bc=BintestH.GetBinContent(b+1)
            #if bc==0.0 or bc==0:
              #hasEmptyBin=True
              #break
          #if hasEmptyBin==True:
            #if currentNbins>bestNbins:
              #foundBestBinning=True
              #print "best bins for this sample ", bestNbins
            #currentNbins-=1
          #elif hasEmptyBin==False:
            #bestNbins=currentNbins
            #currentNbins+=1
          ##if loopcount>10:
            ##exit(0)
        #if bestNbins>maxNbins:
          #maxNbins=bestNbins
        
        
        #f.Close()
        #bufferfile.Close()
      
      #maxNbins=min(maxNbins,nBins)
      #print "HistoConfig ", maxNbins, minX-.01, maxX+.01
      #return maxNbins, minX-.01, maxX+.01 
      
      
      
#---------------------------------------------------------------------------------------## similar class as above but without BDT training
##should probide same functionality as Ohio scripts
class LJWriter:
    def __init__(self,samples,data,systematics):
        self.samples=samples
        self.data=data
        self.systematics=systematics

    
    def fillHisto(self,outfile,histoname,path,weightname="",scale=1.,nBins=10,minX=-1.0,maxX=1.0):
        #ROOT.gDirectory.cd('PyROOT:/')
        histo = ROOT.TH1F(histoname,histoname,nBins,minX,maxX)
        print path
        nless=0
        n4=0
        n5=0
        n6=0
        f = ROOT.TFile( path )
        tree     = f.Get("MVATree")
        # init variables
        BDToutput = array('f', [0])
                     
        tree.SetBranchAddress( "BDTOhio_v2_output", BDToutput )
        # init weight
        weight=array('f',[1.])
        njets=array('i',[1])
        tree.SetBranchAddress("N_Jets",njets)
        csv0=array('f',[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
        tree.SetBranchAddress("CSV",csv0)

        tree.SetBranchAddress( "Weight", weight )
        sysweight=array('f',[1.])
        if weightname!="" :
            tree.SetBranchAddress( weightname, sysweight )
        
        # event loop
        nEvents=tree.GetEntries()
        print type(nEvents), nEvents
        for ievt in range(nEvents):
            #print type(ievt)
            tree.GetEntry(ievt)
            if ievt%1000 ==0:
              print "at event ", ievt
            #print csv0[0]
            if abs(csv0[0])>1.0:
              print "skipping event with csv>>1"
              continue
            output = BDToutput[0]
            if output<=-2.0:
              continue
            sysweight_1=sysweight[0]
            if "ttbar_0p" in histoname:
              n4+=1
              if njets[0]!=4:
                n4-=1
                sysweight_1=1.0
            if "ttbar_1p" in histoname:
              n5+=1
              if njets[0]!=5:
                n5-=1
                sysweight_1=1.0
            if "ttbar_2p" in histoname:
              n6+=1
              if njets[0]<6:
                n6-=1
                sysweight_1=1.0
            if "ttbar_less" in histoname:
              nless+=1
              if njets[0]>3:
                nless-=1
                sysweight_1=1.0
            histo.Fill(output,weight[0]*sysweight_1*scale)
        outfile.cd()
        histo.Write()
        print 'filled '+histoname+', integral: '+str(histo.Integral())
        #print n4, n5, n6, nless
        #f.Close()
        return histo.Integral()
        
    def doBinStatistics(self, outfile, path,category,datacard,nBins=10,minX=-1.0,maxX=1.0):
      bkgSum_histo=None
      
      data_hist=ROOT.TH1F("data_hist","data_hist",nBins,minX,maxX)
      data_hist.Sumw2()
      f = ROOT.TFile(self.data.path)
      tree     = f.Get("MVATree")
      # init variables
      BDToutput = array('f', [0])
      tree.SetBranchAddress( "BDTOhio_v2_output", BDToutput )
      # init weight
      weight=array('f',[1.])
      tree.SetBranchAddress( "Weight", weight )
      for ievt in range(tree.GetEntries()):
            tree.GetEntry(ievt)
            output = BDToutput[0]
            data_hist.Fill(output,weight[0]*self.data.scale)
      f.Close()
      
      sig_hist=ROOT.TH1F("sig_hist","sig_hist",nBins,minX,maxX)
      sig_hist.Sumw2()
      f = ROOT.TFile(self.samples[0].path)
      tree     = f.Get("MVATree")
      # init variables
      BDToutput = array('f', [0])
      tree.SetBranchAddress( "BDTOhio_v2_output", BDToutput )
      # init weight
      weight=array('f',[1.])
      tree.SetBranchAddress( "Weight", weight )
      for ievt in range(tree.GetEntries()):
            tree.GetEntry(ievt)
            output = BDToutput[0]
            sig_hist.Fill(output,weight[0]*self.samples[0].scale)
      f.Close()
      
      bkg_histos=[]
      i=0
      for sample in self.samples:
        if sample.name=="tth":
          continue
        bkg_histos.append(ROOT.TH1F(sample.name,sample.name,nBins,minX,maxX))
        bkg_histos[i].Sumw2()
        f = ROOT.TFile(sample.path)
        tree     = f.Get("MVATree")
      # init variables
        BDToutput = array('f', [0])
        tree.SetBranchAddress( "BDTOhio_v2_output", BDToutput )
      # init weight
        weight=array('f',[1.])
        

        tree.SetBranchAddress( "Weight", weight )
        for ievt in range(tree.GetEntries()):
            tree.GetEntry(ievt)
            output = BDToutput[0]
            bkg_histos[i].Fill(output,weight[0]*sample.scale)
        f.Close()
        print len(bkg_histos), bkg_histos[i].Integral() 
      #do background sum
        if bkgSum_histo:
          bkgSum_histo.Add(bkg_histos[i])
        else:
          bkgSum_histo = bkg_histos[i].Clone()
        i+=1
        print bkgSum_histo.Integral()
      
      # done reading the histos now check for small bins
      i=0
      for sample in self.samples:
        
        if sample.name=="tth":
          continue
        hist=bkg_histos[i].Clone()
        print i
        for b in range(1,nBins+1):
          data = data_hist.GetBinContent(b)
          data_err = data_hist.GetBinError(b)
          sig = sig_hist.GetBinContent(b)
          sig_err = sig_hist.GetBinError(b)
          bkg = bkgSum_histo.GetBinContent(b)
          bkg_err = bkgSum_histo.GetBinError(b)
          val = hist.GetBinContent(b)
          val_err = hist.GetBinError(b)
          
          other_frac = ROOT.TMath.Sqrt(bkg_err**2 - val_err**2)
          print sample.name, category, bkg, bkg_err, sig, sig_err, data, data_err
          print sample.name, category, val, val_err, bkg_err, data_err/5., other_frac/bkg_err, sig/bkg

          #Changed from data_err/3 -> data_err/5 and sig/bkg < 0.02 -> 0.01 - KPL
          if val < .01 or bkg_err < data_err / 5. or other_frac / bkg_err > .95 or sig / bkg < .01:
            continue
          hist_up=hist.Clone("output_Stat"+category+"_"+sample.name+"_AnnBin_"+str(b)+"Up_"+sample.name)
          hist_down=hist.Clone("output_Stat"+category+"_"+sample.name+"_AnnBin_"+str(b)+"Down_"+sample.name)
          hist_down.GetSumw2().Set(0)
          hist_up.GetSumw2().Set(0)
          newValUp=val + val_err
          newValDown=val - val_err
          if newValDown<=0:
            newValDown=0.00001
            print "!! setting statdown bin to ", newValDown
          hist_up.SetBinContent(b, newValUp)
          hist_down.SetBinContent(b, newValDown)                   
             
          outfile.cd()
          hist_up.Write()
          hist_down.Write()
          print "wrote ", "output_Stat"+category+category+"_"+sample.name+"_AnnBin_"+str(b)
          datacard.write("Stat"+category+"_"+sample.name+"_AnnBin_"+str(b)+'\t')
          datacard.write('shape\t')
          for s in self.samples:
              if s.name==sample.name:
                 datacard.write('1')
                 datacard.write('\t')
              else:
                datacard.write('-')
                datacard.write('\t')
          datacard.write('\n')
        i+=1
              
              
              
    def writeline(self,datacard):
        datacard.write('----------------------------------------------------------------------------------------------------\n')

    def writeheader(self,datacard,category, Analysis ,observed):
        datacard.write('imax 1 number of channels\n')
        datacard.write('jmax * number of backgrounds\n')
        datacard.write('kmax * number of nuisance parameters\n')
        self.writeline(datacard)
        datacard.write('bin\tC'+category+'\n')
        datacard.write('observation\t'+str(observed)+'\n')
        datacard.write('shapes\t*\tC'+category+'\thistos_'+category+'_'+Analysis+'.root\toutput_nominal_$PROCESS\toutput_$SYSTEMATIC_$PROCESS\toutput_$SYSTEMATIC_$PROCESS\n')
        datacard.write('shapes\tdata_obs\tC'+category+'\thistos_'+category+'_'+Analysis+'.root\toutput_data\n')
        self.writeline(datacard)


    def writeprocesses(self,datacard,category):
        datacard.write('bin\t')
        for sample in self.samples:
            datacard.write('C'+category)
            datacard.write('\t')
        datacard.write('\n')

        datacard.write('process\t')
        for sample in self.samples:
            datacard.write(sample.name)
            datacard.write('\t')
        datacard.write('\n')

        datacard.write('process\t')
        for i in range(len(self.samples)):
            datacard.write(str(i))
            datacard.write('\t')
        datacard.write('\n')

    def writerate(self,datacard,rate):
        datacard.write('rate\t')
        for r in rate:
            datacard.write("%.4f" % r)
            datacard.write('\t')
        datacard.write('\n')

    def writeratesys(self,datacard,name,type,size):
        datacard.write(name+'\t')
        datacard.write(type+'\t')
        for sample in self.samples:
            if sample.name in size:
                datacard.write(str(size[sample.name]))
            else:
                datacard.write('-')
            datacard.write('\t')
        datacard.write('\n')

    def writeshapesys(self,datacard,systematics):
        for systematic in systematics:
            if "Q2Scale" in systematic.name:
              continue
            datacard.write(systematic.name+'\t')
            datacard.write('shape\t')
            for sample in self.samples:
                datacard.write('1')
                datacard.write('\t')
            datacard.write('\n')
    
    def writelnNsys(self,datacard,cat=""):
        datacard.write('lumi\tlnN\t1.045\t1.045\t1.045\t1.045\t1.045\t1.045\n')
        #datacard.write('CMS_tth_eff_lep\tlnN\t1.014\t1.014\t1.014\t1.014\t1.014\t1.014\t1.014\t1.014\t1.014\n')
        #datacard.write('QCDscale_V\tlnN\t-\t-\t-\t-\t-\t-\t1.013\t1.012\t-\n')
        #datacard.write('QCDscale_VV\tlnN\t-\t-\t-\t-\t-\t-\t-\t-\t1.036\n')
        
        
        #datacard.write('Q2Scale_ttbar_bb\tshape\t-\t1\t-\t-\t-\t-\t-\t-\t-\n')
        #datacard.write('Q2Scale_ttbar_b\tshape\t-\t-\t1\t-\t-\t-\t-\t-\t-\n')
        #datacard.write('Q2Scale_ttbar_cc\tshape\t-\t-\t-\t1\t-\t-\t-\t-\t-\n')
        #if cat=="44" or cat=="43":
           #datacard.write('Q2Scale_ttbar_0p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_1p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_2p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_V\tlnN\t-\t-\t-\t-\t-\t-\t1.477\t1.477\t-\n')
           #datacard.write('Q2Scale_ttbar_less\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')


        #if cat=="54" or cat=="53":
           #datacard.write('Q2Scale_ttbar_0p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_1p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_2p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_V\tlnN\t-\t-\t-\t-\t-\t-\t1.618\t1.618\t-\n')
           #datacard.write('Q2Scale_ttbar_less\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')

        #if cat=="64" or cat=="63" or cat=="62":
           #datacard.write('Q2Scale_ttbar_0p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_1p\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_2p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_V\tlnN\t-\t-\t-\t-\t-\t-\t1.766\t1.766\t-\n')
           #datacard.write('Q2Scale_ttbar_less\tshape\t-\t-\t-\t-\t-\t-\t-\t-\t-\n')

        #if cat=="boosted" or cat=="DB" or cat=="SBT" or cat=="SBH":
           #datacard.write('Q2Scale_ttbar_0p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_1p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_2p\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_ttbar_less\tshape\t-\t-\t-\t-\t1\t-\t-\t-\t-\n')
           #datacard.write('Q2Scale_V\tlnN\t-\t-\t-\t-\t-\t-\t1.766\t1.766\t-\n')

        #datacard.write('QCDscale_tth\tlnN\t1.067\t-\t-\t-\t-\t-\t-\t-\t-\n')
        datacard.write('QCDscale_ttbar\tlnN\t-\t1.03\t1.03\t1.03\t1.03\t1.03\n')
        datacard.write('pdf_gg\tlnN\t1.083\t1.026\t1.026\t1.026\t1.026\t1.026\n')
        datacard.write('pdf_qqbar\tlnN\t-\t-\t-\t-\t-\t-\n')
        datacard.write('pdf_qg\tlnN\t-\t-\t-\t-\t-\t-\n')

        #datacard.write('CMS_res_j\tlnN\t1.015\t1.015\t1.015\t1.015\t1.015\t1.015\n')
        #datacard.write('CMS_tth_pu\tlnN\t1.01\t1.01\t1.01\t1.01\t1.01\t1.01\n')

    def runLJ(self, category="", Analysis="" ):
        nBins, minX, maxX = self.GetHistoConfig(category)
        
        nominal_integrals=[]
        outfile=ROOT.TFile( "output/histos_"+category+"_"+Analysis+".root" ,"recreate")
        observed=self.fillHisto(outfile,"output_data",self.data.path,"",self.data.scale ,nBins, minX, maxX)
        print "ok"
        for sample in self.samples:
            print sample.name
            h="output_nominal_"+sample.name
            p=sample.path
            w=""
            s=sample.scale
            integral=self.fillHisto(outfile,h,p,w,s,nBins, minX, maxX)
            #self.fillTree(p,sample.path.replace(".root","_output.root"))
            nominal_integrals.append(integral)

            for sys in self.systematics:
                #print sys.name
                if sys.name=="Q2Scale_ttbar_bb" and sample.name!="ttbar_bb":
                  continue
                if sys.name=="Q2Scale_ttbar_b" and sample.name!="ttbar_b":
                  continue
                if sys.name=="Q2Scale_ttbar_cc" and sample.name!="ttbar_cc":
                  continue
                if (sys.name=="Q2Scale_ttbar_0p" or sys.name=="Q2Scale_ttbar_1p" or sys.name=="Q2Scale_ttbar_2p" or sys.name=="Q2Scale_ttbar_less") and sample.name!="ttbar_light":
                  continue            
                
                if sys.name_up!="":
                    h="output_"+sys.name_up+"_"+sample.name
                    if sys.samplesuffix_up!="":
                      p=sample.path.replace("_nominal.root",sys.samplesuffix_up+".root")
                    else:
                      p=sample.path.replace(".root",sys.samplesuffix_up+".root")
                    w=sys.weight_up
                    s=sample.scale
                    integral=self.fillHisto(outfile,h,p,w,s,nBins, minX, maxX)

                               
                if sys.name_down!="":
                    h="output_"+sys.name_down+"_"+sample.name
                    if sys.samplesuffix_down!="":
                      p=sample.path.replace("_nominal.root",sys.samplesuffix_down+".root")
                    else:
                      p=sample.path.replace(".root",sys.samplesuffix_down+".root")
                    w=sys.weight_down
                    s=sample.scale
                    self.fillHisto(outfile,h,p,w,s,nBins, minX, maxX)
                    
        datacard=open('datacard.txt','w')
        self.writeheader(datacard,category,Analysis,"%.4f" %observed)
        self.writeprocesses(datacard,category)            
        self.writerate(datacard,nominal_integrals)
        self.writeline(datacard)
        #self.writeshapes
        for sample in self.samples:
            if sample.constraint > 0:
                self.writeratesys(datacard,"QCDscale_"+sample.name,"lnN",{sample.name:1.+sample.constraint})
        self.writelnNsys(datacard,category)
        self.writeshapesys(datacard,self.systematics)
        #self.doBinStatistics(outfile, p,category,datacard ,nBins, minX, maxX)
        datacard.close()
        outfile.Close()
        datacardname="output/datacard_"+category+"_"+Analysis+".txt"
        call(['cp','datacard.txt',datacardname])
        file = open("output/Limit_"+category+"_"+bdtversion+".txt","w")
        #call(['combine','-v','0','-M', 'ProfileLikelihood' ,'datacard.txt', '-t' ,'10'],stdout=file)
        call(['combine','-v','0','-M', 'Asymptotic','--minosAlgo','stepping' ,'datacard.txt', '--run=blind'],stdout=file)
        file.close()


    def GetHistoConfig(self, category):
      print "getting histo binning"
      minX=-0.0
      maxX=0.0
      nBins=10
      for sample in self.samples:
        print sample.name
        f = ROOT.TFile( sample.path )
        tree     = f.Get("MVATree")
        x1=tree.GetMinimum("BDTOhio_v2_output")
        x2=tree.GetMaximum("BDTOhio_v2_output")
        print x1, x2
        f.Close()
        if x1<=minX:
          minX=x1
        if x2>=maxX:
          maxX=x2
        f.Close()
      if minX<-1.0:
         minX=-1.0
      if maxX>1.0:
         maxX=1.0
      if category=="43":
        nBins=20
      elif category=="44":
        nBins=10
      elif category=="53":
        nBins=20
      elif category=="54":
        nBins=10
      elif category=="62":
        nBins=20
      elif category=="63":
        nBins=20
      elif category=="64":
        nBins=10
      else:
        nBins = 10
      print "HistoConfig ", nBins, minX-.01, maxX+.01
      return nBins, minX-.01, maxX+.01 
          
      
