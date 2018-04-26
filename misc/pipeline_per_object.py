# Quick script to run pipeline over multiple objects
import os
import glob
import sys

objects = ['test_aquila.lst']

filein = '/scratch/david/master_project/scripts/misc/paths.txt'
fileout = '/scratch/david/master_project/scripts/subscripts/paths.py'

f = open(filein,'r')
filedata = f.read()
f.close()

for arg in sys.argv[1:]:
    newdata = filedata.replace("OBJECT",arg)

    f = open(fileout,'w')
    f.write(newdata)
    f.close()

    try:
        print '====================='*2
        print 'NEW DATA SERIES:', arg
        print '====================='*2
        os.system('nice -n 19 python main_pipeline.py')
    except:
        continue
