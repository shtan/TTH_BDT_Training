module use -a /afs/desy.de/group/cms/modulefiles/
module load cmssw/slc6_amd64_gcc530

alias pyhton='python'

myvarcwd=$PWD
cd /nfs/dust/cms/user/kelmorab/CMSSW_Moriond2017/cardsCMSSWv2/CMSSW_8_0_26_patch2/src
cmsenv
cd ~
echo "setupCMSSW_8026_patch2 and stuff"
alias root='root -l'
cd $myvarcwd

