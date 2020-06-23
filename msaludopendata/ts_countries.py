import pandas as pd
import numpy as np
import os
import datetime
from common import *

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

def us_ts(csv_file):
    assert False
    df_us = pd.read_csv(csv_file)
    df_us['LOCATION']=df_us['iso3'].apply(normalize_str)
    df_us=df_us[[c for c in df_us.columns if c.count('/')>0 or c=='LOCATION']]
    df_us=df_us.groupby('LOCATION').sum()
    df_us=iso_date(df_us)
    return df_us

def ts_countries(dict_location_to_iso):
    df_confirmed = concat_time_series([global_ts(DATA_IN_CSV_CONFIRMADOS_WORLD)]).reset_index()
    df_confirmed['TYPE']='CONFIRMADOS'
    df_death = concat_time_series([global_ts(DATA_IN_CSV_MUERTOS_WORLD)]).reset_index()
    df_death['TYPE']='MUERTOS'
    df = concat_time_series([df_confirmed.set_index(['TYPE', 'LOCATION']),df_death.set_index(['TYPE', 'LOCATION'])]).reset_index()
    df['LOCATION']=df['LOCATION'].apply(lambda l : dict_location_to_iso.get(l,l))
    df=df.set_index(['TYPE', 'LOCATION'])
    return df
