import pandas as pd
import os
import paths

def create_db():

    if os.path.exists(paths.database):
        print 'WARNING: OVERWRITING DATABASE'

    with open(paths.obsid_list,'r') as f:
        obsids = [l.strip() for l in f.readlines()]

    db = pd.DataFrame({'obsids':obsids})
    db.to_csv(paths.database)


def add_info():
    db.loc[:,'f'] = p.Series(np.random.randn(sLength), index=db.index)
    return None


if not os.path.exists(paths.database):
    create_db()
