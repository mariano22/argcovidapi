"""
Quedarse con la ultima imagen de las series temporales y producir tablas con
las siguientes columnas: (LOCATION, LAST_UPDATE, CFR, CONFIRMADOS, ...)
Y guarda las tablas en 3 archivos (construct_tables):
- Por paises
- Por provincias
- Por departamentos
"""
import pandas as pd
import numpy as np
import os
import datetime

import download
import time_series
import info_df
import info_gdf
from common import *
from saliomapita_dependency import *

def final_time_series(ts):
    """
    Dada una serie temporal (indice: TYPE, LOCATION y columnas: DATES)
    retorna una imagen de la ultima fecha (y CFR, CONFIRMADOS, MUERTOS, etc queda
    en las columnas).
    """
    ts = ts.reset_index()
    # 'anti-pivot' (indice: TYPE, LOCATION y columnas: DATES) -> (TYPE, LOCATION, date, value)
    ts = pd.melt(ts, id_vars=['TYPE','LOCATION'], value_vars=ts.columns[2:], var_name='date')
    # (TYPE, LOCATION, date, value) -> (LOCATION, date, CFR, CONFIRMADOS, MUERTOS, etc)
    ts = ts.pivot_table(index=['LOCATION','date'], columns='TYPE', values='value').reset_index()
    # Get the last date values only
    ts['date']=ts['date'].apply(lambda d : pd.to_datetime(d,format=DATE_FORMAT))
    last_date = max(ts['date'])
    df_final = ts[ts['date']==last_date].copy()
    df_final['date']=df_final['date'].apply(lambda d : d.strftime(DATE_FORMAT))
    df_final = df_final.rename(columns={'date':'LAST_UPDATE'})
    # Merge with info_df (setting LAT, LONG, POPULATION, AREA)
    df_final = pd.merge(df_final,info_df.GLOBAL_INFO_DF,on='LOCATION',how='left')
    return df_final

def add_with_nulls(df,df_info,level_count):
    df_info = df_info[df_info['LOCATION'].apply(lambda l : l.count('/')==level_count)]
    df = pd.merge(df,df_info['LOCATION'],on='LOCATION',how='outer').fillna(0)
    return df

def save_restricted_map(gdf,df,map_filename):
    gdf[gdf['LOCATION'].apply(lambda l : l in set(df['LOCATION']))].to_file(map_filename, driver='GeoJSON')

def construct_tables():
    LEVEL_MAPS = [ ('provinces', 1),
                   ('departments', 2) ]
    df_arg = final_time_series(time_series.time_series_arg())
    for level_name, level_count in LEVEL_MAPS:
        df_filtered = df_arg[df_arg['LOCATION'].apply(lambda l : l.count('/')==level_count)]
        df_filtered = add_with_nulls(df_filtered, info_df.GLOBAL_INFO_DF, level_count)
        df_filtered = add_min_dist(df_filtered)
        df_filtered.to_csv(CSV_TEMPLATE.format(level_name),index=False)
        save_restricted_map(info_gdf.GLOBAL_INFO_GDF, df_filtered, GEOJSON_TEMPLATE.format(level_name))
    df_countries = final_time_series(time_series.time_series_countries())
    df_countries = add_min_dist(df_countries)
    df_countries.to_csv(CSV_TEMPLATE.format('countries'),index=False)
    save_restricted_map(info_gdf.GLOBAL_INFO_GDF, df_countries, GEOJSON_TEMPLATE.format('countries'))

if __name__ == '__main__':
    download.download_csvs()
    construct_tables()
