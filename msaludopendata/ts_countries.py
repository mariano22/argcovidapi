import pandas as pd
import numpy as np
import os
import datetime
from common import *

def global_ts(csv_file):
    df_global = pd.read_csv(csv_file)
    df_global['LOCATION']=df_global['Country/Region'].apply(normalize_str)
    df_global=df_global[[c for c in df_global.columns if c.replace('/','').isdigit() or c=='LOCATION']]
    return df_global

def us_ts(csv_file):
    df_us = pd.read_csv(csv_file)
    df_us['LOCATION']=df_us['iso3'].apply(normalize_str)
    df_us=df_us[[c for c in df_us.columns if c.count('/')>0 or c=='LOCATION']]
    return df_us

def ts_countries(dict_location_to_iso):
    df_confirmed = pd.concat([us_ts(DATA_IN_CSV_CONFIRMADOS_US),global_ts(DATA_IN_CSV_CONFIRMADOS_WORLD)],ignore_index=False)
    df_confirmed['TYPE']='CONFIRMADOS'
    df_death = pd.concat([us_ts(DATA_IN_CSV_MUERTOS_US),global_ts(DATA_IN_CSV_MUERTOS_WORLD)],ignore_index=False)
    df_death['TYPE']='MUERTOS'
    df = pd.concat([df_confirmed,df_death],ignore_index=False)
    df['LOCATION']=df['LOCATION'].apply(lambda l : dict_location_to_iso.get(l,l))
    df = df.groupby(['TYPE','LOCATION']).sum()
    df = correct_time_series(df)
    df = df.rename(columns=lambda c: pd.to_datetime(c,format='%m/%d/%y').strftime(DATE_FORMAT))
    return df
