# Quick script to run pipeline over multiple objects
import os
import glob
import subprocess
import os

objects = ['4U_0614p09',
            '4U_1636_m53',
            '4U_1702m43',
            '4u_1705_m44',
            '4U_1728_34',
            'aquila_X1',
            'cen_x1',
            'cir_x1',
            'cyg_x2',
            'EXO_0748_676',
            'gx_17p2',
            'gx_339_d4',
            'gx_340p0',
            'gx_349p2',
            'gx_3p1',
            'gx_5m1',
            'H1743m322',
            'HJ1900d1_2455',
            'IGR_J00291p5934',
            'IGR_J17480m2446',
            'IGR_J17498m2921',
            'IGR_J17511m3057',
            'J1701_462',
            'J17511m3057',
            'KS_1731m260',
            'sco_x1',
            'sgr_x1',
            'sgr_x2',
            'S_J1756d9m2508',
            'v4634_sgr',
            'XB_1254_m690',
            'xte_J0929m314',
            'xte_J1550m564',
            'xte_J1751m305',
            'xte_J1807m294',
            'xte_J1808_369',
            'xte_J1814m338',
            'xte_J2123_m058']

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
        command = 'python main_pipeline.py'
        os.system(command)
    except:
        continue