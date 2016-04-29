# Quick script to run pipeline over multiple objects
import os
import glob
import subprocess
import os

objects = ['4u_1705_m44',
          'xte_J1808_369',
          'cir_x1',
          'EXO_0748_676',
          'HJ1900d1_2455',
          'v4634_sgr',
          '4U_1728_34',
          '4U_0614p09',
          '4U_1702m43',
          'J1701_462',
          'aquila_X1',
          '4U_1636_m53',
          'cyg_x2',
          'gx_5m1',
          'gx_340p0',
          'sco_x1',
          'gx_17p2',
          'gx_349p2']

filein = '/scratch/david/master_project/scripts/misc/paths.txt'
fileout = '/scratch/david/master_project/scripts/subscripts/paths.py'

f = open(filein,'r')
filedata = f.read()
f.close()

for o in objects:
    newdata = filedata.replace("OBJECT",o)

    f = open(fileout,'w')
    f.write(newdata)
    f.close()

    try:
        print '====================='*2
        print 'NEW DATA SERIES:', o
        print '====================='*2
        command = ['nice -n 19 python main_pipeline.py']

        p = subprocess.Popen(' '.join(command), stdout=subprocess.PIPE, shell=True)
        p.wait()
        p.stdout.read()
    except Exception, e:
        print str(e)
        continue
