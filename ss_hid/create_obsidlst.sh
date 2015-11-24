#!/bin/bash
cut -d'|' -f2 targets.lst > obsids.lst
sed -i -e 1,5d obsids.lst
for i in obsids.lst
do
  sed '/^ /d' $i > $i.out
  mv  $i.out $i
done
