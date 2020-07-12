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
    """ Convert from JOHNHOPKINS_DATE_FORMAT to common.DATE_FORMAT """
    ts=ts.rename(columns = lambda d : pd.to_datetime(d,format=JOHNHOPKINS_DATE_FORMAT).strftime(DATE_FORMAT))
    return ts

def global_ts(csv_file):
    df_global = pd.read_csv(csv_file)
    df_global['LOCATION']=df_global['Country/Region'].apply(normalize_str)
    # Drop all columns but LOCATION and dates
    df_global=df_global[[c for c in df_global.columns if c.replace('/','').isdigit() or c=='LOCATION']]
    df_global=df_global.groupby('LOCATION').sum()
    df_global=iso_date(df_global)
    return df_global

def ts_countries():
    df_confirmed = correct_ts(global_ts(DATA_IN_CSV_CONFIRMADOS_WORLD)).reset_index()
    df_death = correct_ts(global_ts(DATA_IN_CSV_MUERTOS_WORLD)).reset_index()
    df_recovered = correct_ts(global_ts(DATA_IN_CSV_RECOVERED_WORLD)).reset_index()

    df_confirmed['TYPE']='CONFIRMADOS'
    df_death['TYPE']='MUERTOS'
    df_recovered['TYPE']='RECUPERADOS'
    df_confirmed=df_confirmed.set_index(['TYPE', 'LOCATION'])
    df_death=df_death.set_index(['TYPE', 'LOCATION'])
    df_recovered=df_recovered.set_index(['TYPE', 'LOCATION'])
    df = concat_time_series([df_confirmed,df_death,df_recovered])

    df_actives = df.loc['CONFIRMADOS']-df.loc['RECUPERADOS']-df.loc['MUERTOS']

    df_actives=df_actives.reset_index()
    df_actives['TYPE']='ACTIVOS'
    df_actives=df_actives.set_index(['TYPE', 'LOCATION'])
    df = concat_time_series([df,df_actives])
    df = df[df.index.get_level_values(0)!='RECUPERADOS']

    df = df.reset_index()
    df['LOCATION']=df['LOCATION'].apply(lambda l : info_df.GLOBAL_LOCATION_TO_ISO_COUNTRIES.get(l,l))
    df=df.set_index(['TYPE', 'LOCATION'])

    return df
