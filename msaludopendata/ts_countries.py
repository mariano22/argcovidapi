"""
Produce la serie temporal (acumulada) del mundo.
Output functions: ts_countries
"""
import pandas as pd
import numpy as np
import os
import datetime
from common import *
import info_df

JOHNHOPKINS_DATE_FORMAT = "%m/%d/%y"
def iso_date(ts):
    ts=ts.rename(columns = lambda d : pd.to_datetime(d,format=JOHNHOPKINS_DATE_FORMAT).strftime(DATE_FORMAT))
    return ts

def global_ts(csv_file):
    df_global = pd.read_csv(csv_file)
    df_global['LOCATION']=df_global['Country/Region'].apply(normalize_str)
    df_global=df_global[[c for c in df_global.columns if c.replace('/','').isdigit() or c=='LOCATION']]
    df_global=df_global.groupby('LOCATION').sum()
    df_global=iso_date(df_global)
    return df_global

def ts_countries():
    df_confirmed = concat_time_series([global_ts(DATA_IN_CSV_CONFIRMADOS_WORLD)]).reset_index()
    df_confirmed['TYPE']='CONFIRMADOS'
    df_death = concat_time_series([global_ts(DATA_IN_CSV_MUERTOS_WORLD)]).reset_index()
    df_death['TYPE']='MUERTOS'
    df = concat_time_series([df_confirmed.set_index(['TYPE', 'LOCATION']),df_death.set_index(['TYPE', 'LOCATION'])]).reset_index()
    df['LOCATION']=df['LOCATION'].apply(lambda l : info_df.GLOBAL_LOCATION_TO_ISO_COUNTRIES.get(l,l))
    df=df.set_index(['TYPE', 'LOCATION'])
    return df
