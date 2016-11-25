import os
import glob

for o in glob.glob('/scratch/david/master_project/scripts/plots/*.py'):
    
    filein = o
    fileout = o

    f = open(filein,'r')
    filedata = f.read()
    f.close()

    newdata = filedata.replace("ordering = ['gx1','event','binned','std2']","ordering = ['gx1','gx2','event','binned','std2']")

    f = open(fileout,'w')
    f.write(newdata)
    f.close()
