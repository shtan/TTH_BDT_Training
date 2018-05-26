#!/bin/bash

perms=("noreco" "perm0" "perm1" "perm2" "perm3")

namee=apr14_allbackgrounds

for perm in "${perms[@]}"
do
    echo $perm

    python OnlyTrain.py $perm 64 $namee ./bdtconfigs/64_S17V2.txt /eos/user/s/shtan/storageforbatch/stage35stuff/apr2/combined_totrain_apr14/ test
    
    python OnlyTrain.py $perm 63 $namee ./bdtconfigs/63_S17V2.txt /eos/user/s/shtan/storageforbatch/stage35stuff/apr2/combined_totrain_apr14/ test
done

