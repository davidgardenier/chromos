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


def merge(db, df, columns):
    '''
    Careful with merging not to lose any data. This method checks whether it is
    merely an update of the database, or an extension.

    Arguments:
     - Main database (pandas dataframe)
     - New database (pandas dataframe)
     - Columns to be overwritten if already existing (list)

    Output:
     - Updated main database
    '''

    # Check if dataframe has values
    if df.shape[0]==0:
        return db

    # Remove unnamed columns from merges
    for col in db.columns:
       if 'Unnamed' in col:
           del db[col]

    # Allow previously calculated columns to be overwritten
    for c in columns:
        if c in db:
            del db[c]

    db = db.drop_duplicates()
    # Ensuring any duplicates for instance in Phil's xtescan2 are removed
    df = df.drop_duplicates()

    ns = [n for n in df if n in db]
    db = pd.merge(db,df, on=ns, how='left')
    return db


def save(db,location=paths.database):
    # Remove unnamed columns from merges
    for col in db.columns:
       if 'Unnamed' in col:
           del db[col]
    db.drop_duplicates()
    db.to_csv(location)


if not os.path.exists(paths.database):
    create_db()
