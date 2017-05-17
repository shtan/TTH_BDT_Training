import os
import stat
import sys

def create_script(configpath,cmsswpath,version,category,trainpath,treepath):
    script='#!/bin/bash\n'
    script+='export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch\n'
    script+='source $VO_CMS_SW_DIR/cmsset_default.sh\n'
    script+='cd '+cmsswpath+'src\neval `scram runtime -sh`\n'
    script+='cd '+trainpath+'\n'
    script+='python OnlyTrain.py '+category+' '+version+' '+configpath+version+'/'+category+'_'+'S17V1'+'.txt '+treepath+' test' 
    filename='scripts/'+'train_'+'Spring17_'+version+'_'+category+'.sh'
    f=open(filename,'w')
    f.write(script)
    f.close()
    st = os.stat(filename)
    os.chmod(filename, st.st_mode | stat.S_IEXEC)



configpath="bdtconfigs/"
trainpath=os.getcwd()
treepath="/nfs/dust/cms/user/kelmorab/SplitTrees2702_Spring17_V3"
categories=["43","44","53","54","62","63","64"]
versions=["Spring17v1"]
cmsswpath="/nfs/dust/cms/user/kelmorab/CMSSW_7_4_15/"

if not os.path.exists("logs"):
    os.makedirs("logs")
if not os.path.exists("scripts"):
    os.makedirs("scripts")
    
for version in versions:
    for category in categories:
        create_script(configpath,cmsswpath,version,category,trainpath,treepath)
        
    