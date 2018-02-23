import sys

infilename=sys.argv[1]
outfilename=sys.argv[2]


inf=open(infilename,"r")
outf=open(outfilename,"w")

inlist=list(inf)
nlines=len(inlist)
il=0
for line in inlist:
  il+=1
  newline=line
  if "BDT_common5_input_" in line:
    newline=line.replace("BDT_common5_input_","")
  if "Evt_blr_ETH_transformed" in line:
    newline=line.replace("Evt_blr_ETH_transformed","blr_transformed")
  outf.write(newline)

outf.close()
inf.close()
    