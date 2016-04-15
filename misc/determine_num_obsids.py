import os
import glob
import operator

os.chdir('/scratch/david/master_project/obsid_lists')
names={}
for fn in glob.glob('*.lst'):
    with open(fn) as f:
        names[fn]=sum(1 for line in f if line.strip() and not line.startswith('#'))

sortednames = sorted(names.items(), key=operator.itemgetter(1), reverse=True)

for f in sortednames:
    print '{0:<20} {1:>12}'.format(f[0][:-4], f[1])
