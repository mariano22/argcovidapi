import pandas as pd
import numpy as np
import os
import datetime

import time_series
import info_df
import info_gdf
from common import *

def final_time_series(ts=None):
    if ts is None:
        ts = time_series.time_series()
    ts = ts.reset_index()
    ts = pd.melt(ts, id_vars=['TYPE','LOCATION'], value_vars=ts.columns[2:], var_name='date')
    ts = ts.pivot_table(index=['LOCATION','date'], columns='TYPE', values='value').reset_index()
    ts['date']=ts['date'].apply(lambda d : pd.to_datetime(d,format=DATE_FORMAT))
    last_date = max(ts['date'])
    df_final = ts[ts['date']==last_date].copy()
    df_final['date']=df_final['date'].apply(lambda d : d.strftime(DATE_FORMAT))
    df_final = df_final.rename(columns={'date':'LAST_UPDATE'})
    df_final = pd.merge(df_final,info_df.GLOBAL_INFO_DF,on='LOCATION',how='left')
    return df_final

def add_with_nulls(df,df_info,level_count):
    df_info = df_info[df_info['LOCATION'].apply(lambda l : l.count('/')==level_count)]
    df = pd.merge(df,df_info['LOCATION'],on='LOCATION',how='outer').fillna(0)
    return df

def save_restricted_map(gdf,df,map_filename):
    gdf[gdf['LOCATION'].apply(lambda l : l in set(df['LOCATION']))].to_file(map_filename, driver='GeoJSON')

def construct_tables():
    CSV_TEMPLATE = 'data/info_{}.csv'
    GEOJSON_TEMPLATE = 'data/maps_{}.geojson'
    LEVEL_MAPS = [ ('countries', 0, False),
                   ('provinces', 1, True),
                   ('departments', 2, True) ]
    df = final_time_series()
    for level_name, level_count, add_nulls in LEVEL_MAPS:
        df_filtered = df[df['LOCATION'].apply(lambda l : l.count('/')==level_count)]
        if add_nulls:
            df_filtered = add_with_nulls(df_filtered, info_df.GLOBAL_INFO_DF, level_count)
        df_filtered.to_csv(CSV_TEMPLATE.format(level_name),index=False)
        save_restricted_map(info_gdf.GLOBAL_INFO_GDF, df_filtered, GEOJSON_TEMPLATE.format(level_name))

if __name__ == '__main__':
    construct_tables()
