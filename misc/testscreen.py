
import subprocess
import os

objects = ['test1',
           'test2',
           'test3']

for o in objects:
    print o
    command = ['nice -n 19 screen -S "'+o+'" -dm bash -c ". /home/david/maintain_vir_env.sh; nice -n 19 saextrct"']#python main_pipeline.py; python misc/plot_info_per_obsid.py"'

    p = subprocess.Popen(' '.join(command), stdout=subprocess.PIPE, shell=True)
    p.wait()
    p.stdout.read()
