import pandas as pd
import os

# Import file with bursty obsids
path = os.path.dirname(os.path.realpath(__file__))
file_name = path + '/bursts_list.txt'
db_bursts = pd.read_csv(file_name, sep=' ')
obsids_bursts = db_bursts.obsid.values.tolist()


def filter_bursts(df):
    """Filter out bursts found by Phil."""
    df = df[~df['obsids'].isin(obsids_bursts)]
    df = df[~df['obsids'].astype(str).str.startswith('20161')]
    return df
