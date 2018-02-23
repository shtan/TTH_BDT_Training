Use these script to prepare the ntuples for the BDT training.
It will split the ntuples into smaller ones depending on:
- categories you define
- Even/Odd (training/fitting split)
- tt+X flavor

You can configure this by editing Defintions.py

To run the preparation then do 
python OnlyPrepareTrees.py

This will read in the ntuples, write and compile a c++ program and then send some jobs to the batch system
Once all the jobs are done you are good to go

!IMPROTANT!:
The tool will only keep branches that are listen in branchlist.txt 
To get a branchlist.txt for your ntuples do 
python getListOfBranches.py PATHTOONEOFYOURROOTFILES
Then edit the branchlist.txt to remove unneeded branches (will speed up the following training steps)

