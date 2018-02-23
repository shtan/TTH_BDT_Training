#set up everything here



OutputDirectoryForPreparedTrees="/nfs/dust/cms/user/kelmorab/SplitTrees04102017/"

Categories=[
  #["42","(N_LooseLeptons==1 && N_TightLeptons==1 && N_Jets==4 && N_BTagsM==3)"],
  #["52","(N_LooseLeptons==1 && N_TightLeptons==1 && N_Jets==4 && N_BTagsM==3)"],
  ["43","(N_LooseLeptons==1 && N_TightLeptons==1 && N_Jets==4 && N_BTagsM==3)"],
  ["44","(N_LooseLeptons==1 && N_TightLeptons==1 && N_Jets==4 && N_BTagsM==4)"],
  ["53","(N_LooseLeptons==1 && N_TightLeptons==1 && N_Jets==5 && N_BTagsM==3)"],
  ["54","(N_LooseLeptons==1 && N_TightLeptons==1 && N_Jets==5 && N_BTagsM>=4)"],
  ["62","(N_LooseLeptons==1 && N_TightLeptons==1 && N_Jets>=6 && N_BTagsM==2)"],
  ["63","(N_LooseLeptons==1 && N_TightLeptons==1 && N_Jets>=6 && N_BTagsM==3)"],
  ["64","(N_LooseLeptons==1 && N_TightLeptons==1 && N_Jets>=6 && N_BTagsM>=4)"],
]



SystematicTreeNames=["nominal"]

#MCinputDirectory="/nfs/dust/cms/user/kelmorab/trees_Spring17_v2/"
##List of MCSamples
## ["ProcessName", [List of input folders], SplitMode="None" or "EvenOdd" , BOOL UseFlavorSplitting, RateSystematics=[["lumi",1.025],[], ShapeSystematics=[["lumi",1.025],[]]
## the syst parameters do not do anything :)
#MCSamples=[
	##["ttHbb",["ttHbb/ttHbb*nominal*.root"],"EvenOdd","False",[["lumi",1.025],["pdf",1.03]],[]],
	#["ttbar",["ttbar_sl/ttbar_sl*nominal*.root"],"EvenOdd","False",[["lumi",1.025],["pdf",1.03]],[]],
	
#]

MCinputDirectory="/nfs/dust/cms/user/kelmorab/trees_Spring17_v5/"
#List of MCSamples
# ["ProcessName", [List of input folders], SplitMode="None" or "EvenOdd" , BOOL UseFlavorSplitting, RateSystematics=[["lumi",1.025],[], ShapeSystematics=[["lumi",1.025],[]]
# the syst parameters do not do anything :)
MCSamples=[
	["ttHbb",["ttH*/ttH*nominal*.root"],"EvenOdd","False",[["lumi",1.025],["pdf",1.03]],[]],
	["ttbar",["ttbar_*/ttbar*nominal*.root"],"EvenOdd","False",[["lumi",1.025],["pdf",1.03]],[]],
	
]


DataSamples=[]
DATAinputDirectory=""
