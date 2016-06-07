from astroquery.simbad import Simbad
import numpy as np
from collections import defaultdict


def latextab(tab):
    return '&'.join(tab) + '\\\\'


def getnames(o):
    d = defaultdict(list)
    
    result_table = np.array(Simbad.query_objectids(o)['ID'], dtype='object')
    
    for i, e in enumerate(result_table):
        result_table[i] = ' '.join(e.split())
        d['Source'] = o
        if e.startswith('SWIFT'):
            d['SWIFT'] = e.strip('SWIFT ')
        if e.startswith('XTE'):
            d['XTE'] = e.strip('XTE ')
        if e.startswith('4U'):
            d['4U'] = e.strip('4U ')
        if e.startswith('GX'):
            d['GX'] = e.strip('GX ')
        if e.startswith('X '):
            d['X'] = e.strip('X ')
        if e.startswith('IGR'):
            d['IGR'] = e.strip('IGR ')
        if e.startswith('EXO'):
            d['EXO'] = e.strip('EXO ')
        if e.startswith('INTEGRAL1'):
            d['INTEGRAL1'] = e.strip('INTEGRAL1 ')

    foundnames = [d[s] for s in order]
    for i, f in enumerate(foundnames):
        if type(f) == list:
            foundnames[i] = ' '
    
    return foundnames
    

nss = ['4U 1705-44',
'4U 0614+09',
'4U 1636-53',
'4U 1702-43',
'4U 1728-34',
'Aql X-1',
'Cir X-1',
'Cyg X-2',
'EXO 0748-676',
'GX 5-1',
'GX 17+2',
'GX 340+0',
'GX 349+2',
'HETE J1900.1-2455',
'IGR J00291+5934',
'IGR J17480-2446',
'IGR J17498-2921',
'XTE J1701-462',
'KS 1731-260',
'Sco X-1',
'Sgr X-1',
'Sgr X-2',
'SWIFT J1756.9-2508',
'V4634 Sgr',
'XB 1254-690',
'XTE J0929-314',
'XTE J1751-305',
'XTE J1807-294',
'SAX J1808.4-3658',
'XTE J1814-338']

bhs = ['GX 339-4',
'H1743-322',
'XTE J1550-564']

nss = sorted(nss)
bhs = sorted(bhs)

order = ['Source', '4U', 'GX', 'IGR', 'INTEGRAL1', 'SWIFT','X','XTE']

names_ns = []
names_bh = []

for o in nss:
    ns = getnames(o)
    names_ns.append(latextab(ns))
for o in bhs:
    bh = getnames(o)
    names_bh.append(latextab(bh))

header = []
for e in order:
    header.append('\\tableheadline{' + e + '}')

lines = []
lines.append('\\begin{landscape}')
lines.append('\\begin{longtable}{'+'c'*(len(header))+'} \\toprule')
lines.append(latextab(header))
lines.append('\\midrule')
lines.append('\\endhead')
lines.extend(names_ns)
lines.append('\\midrule')
lines.extend(names_bh)
lines.append('\\bottomrule')
lines.append('\\caption[Alternative source names]{Overview of various alternative sources names as classified by \\citet{SIMBAD}, grouped into neutron stars (above the horizontal line) and black holes (below the horizontal line). The leftmost column gives the source names used throughout this work.}\\label{tab:aka}')
lines.append('\\end{longtable}')
lines.append('\\end{landscape}')

with open('/scratch/david/master_project/tab_names.tex', 'w') as txt:
    txt.write('\n'.join(lines))
