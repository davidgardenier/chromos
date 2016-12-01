import pandas as pd
import os

obj = ['4U_0614p09',
'4U_1636_m53',
'4U_1702m43',
'4u_1705_m44',
'4U_1728_34',
'aquila_X1',
'cir_x1',
'cyg_x2',
'EXO_0748_676',
'gx_17p2',
'gx_340p0',
'gx_349p2',
'gx_5m1',
'HJ1900d1_2455',
'IGR_J00291p5934',
'IGR_J17480m2446',
'IGR_J17498m2921',
'KS_1731m260',
'xte_J1808_369',
'S_J1756d9m2508',
'sco_x1',
'sgr_x1',
'sgr_x2',
'v4634_sgr',
'XB_1254_m690',
'xte_J0929m314',
'J1701_462',
'xte_J1751m305',
'xte_J1807m294',
'xte_J1814m338',
'gx_339_d4',
'H1743m322',
'xte_J1550m564']

def findbestres(res):
    '''Find the smallest resolution from a list of resolutions'''

    # Split resolutions into values and units
    heads = []
    tails = []
    for s in res:
        unit = s.strip('0123456789')
        num = s[:-len(unit)]
        heads.append(num)
        tails.append(unit)

    # Sort by unit, then by value
    unitorder = ['ms','us','s']
    for u in unitorder:
        if u in tails:
            indices = [i for i, x in enumerate(tails) if x==u]
            sameunits = [heads[i] for i in indices]
            sortvalues = sorted(sameunits)
            return sortvalues[0]+u


def findbestdataperobsid(df):
    '''Select the data with best mode and resolution'''
    ordering = ['gx1','gx2','event','binned','std2']
    for mode in ordering:
        if mode in df.modes.values:
            df = df[df.modes==mode]
            if df.shape[0] > 1:
                bestres = findbestres(df.resolutions.values)
                return df[df.resolutions==bestres].iloc[0]
            else:
                return df.iloc[0]


def findbestdata(db):
    # Apply constraint to the data
    db = db[(db.pc1.notnull() & db.lt3sigma==True)]
    db = db.groupby('obsids').apply(findbestdataperobsid)
    return db
    

for o in obj:
    p = '/scratch/david/master_project/' + o + '/info/database_' + o + '.csv'
    db = pd.read_csv(p)
    df = findbestdata(db)
    print '%-20s %d' %(o, len(df))
