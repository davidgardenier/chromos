#!/bin/bash
filename='/scratch/david/master_project/gx_339_d4/info/obsids_lucy_has_but_i_dont.lst'
plots='/scratch/david/master_project/gx_339_d4/info/plots/'
copyto='/scratch/david/master_project/gx_339_d4/info/plots/lucy/'
filelines=`cat $filename`
echo Start
for line in $filelines ; do
    cp $plots$line $copyto$line
done
