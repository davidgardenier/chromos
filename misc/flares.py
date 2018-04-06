"""Extract all burst times with obsid and object."""
import pandas as pd

objects = [('4u_1705_m44', '4U 1705-44'),
           ('4U_0614p09', '4U 0614+09'),
           ('4U_1608m52', '4U 1608-52'),
           ('4U_1636_m53', '4U 1636-53'),
           ('4U_1702m43', '4U 1702-43'),
           ('4U_1728_34', '4U 1728-34'),
           ('aquila_X1', 'Aql X-1'),
           ('cir_x1', 'Cir X-1'),  # strange behaviour
           ('cyg_x2', 'Cyg X-2'),
           ('EXO_0748_676', 'EXO 0748-676'),  # Strange behaviour
           ('gx_5m1', 'GX 5-1'),  # Only 5 points
           ('gx_17p2', 'GX 17+2'),  # Only has 4 points
           ('gx_339_d4', 'GX 339-4'),  # BH system
           ('gx_340p0', 'GX 340+0'),  # Only 5 points
           ('gx_349p2', 'GX 349+2'),  # Only 3 points
           ('HJ1900d1_2455', 'HETE J1900.1-2455'),
           ('IGR_J00291p5934', 'IGR J00291+5934'),
           ('IGR_J17480m2446', 'IGR J17480-2446'),
           ('IGR_J17498m2921', 'IGR J17498-2921'),  # Only 1 point
           ('J1701_462', 'XTE J1701-462'),
           ('KS_1731m260', 'KS 1731-260'),
           ('sco_x1', 'Sco X-1'),
           ('sgr_x1', 'Sgr X-1'),
           ('sgr_x2', 'Sgr X-2'),
           ('S_J1756d9m2508', 'SWIFT J1756.9-2508'),
           ('v4634_sgr', 'V4634 Sgr'),
           ('XB_1254_m690', 'XB 1254-690'),
           ('xte_J0929m314', 'XTE J0929-314'),
           ('xte_J1550m564', 'XTE J1550-564'),  # BH system
           ('xte_J1751m305', 'XTE J1751-305'),
           ('xte_J1807m294', 'XTE J1807-294'),  # Only 4 points
           ('xte_J1808_369', 'SAX J1808.4-3648'),
           ('xte_J1814m338', 'XTE J1814-338')]


def path(o):
    return '/scratch/david/master_project/{}/info/database_{}.csv'.format(o, o)


dfs = []

for o in objects:
    obj = o[0]
    db = pd.read_csv(path(obj))

    try:
        db = db[db.flare_times.notnull()]
    except AttributeError:
        continue

    db = db.filter(items=['obsids', 'flare_times'])
    db = db.drop_duplicates()
    db['source'] = o[1]
    db = db[['source', 'obsids', 'flare_times']]
    dfs.append(db)

db = pd.concat(dfs)
db.to_csv('/scratch/david/master_project/flares.csv')
    # print(obj, db)
