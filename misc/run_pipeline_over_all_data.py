# Quick script to run pipeline over multiple objects
import os
import glob

objects = [#'4u_1705_m44.lst',
           '4U_1636_m53.lst',
           #'aquila_X1.lst',
           'cen_x1.lst',
           'gx_3+1.lst',
           'gx_13+1.lst',
           'J1701_462.lst',
           'sco_x1.lst',
           'v4634_sgr.lst',
           'XB_1254_m690.lst',
           'xte_J2123_m058.lst']

filein = '/scratch/david/master_project/scripts/misc/paths.txt'
fileout = '/scratch/david/master_project/scripts/subscripts/paths.py'

f = open(filein,'r')
filedata = f.read()
f.close()

for o in objects:
    newdata = filedata.replace("OBJECT",o.split('.lst')[0])

    f = open(fileout,'w')
    f.write(newdata)
    f.close()

    try:
        print '====================='*2
        print 'NEW DATA SERIES:', o
        print '====================='*2
        os.system('python main_pipeline.py')
    except:
        continue
