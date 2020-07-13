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
import saliomapita_dependency
import visualization_tools

def final_view(ts):
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

def save_restricted_map(gdf,df,map_filename):
    """ Guarda en map_filename las geoshapes cuyas LOCATION aparecen en df['LOCATION'] """
    location_set = set(df['LOCATION'])
    gdf[gdf['LOCATION'].apply(lambda l : l in location_set)].to_file(map_filename, driver='GeoJSON')

def save_final_view(df, df_name):
    """ Dado un DataFrame con la vista final de cierta granularidad genera los
        .csv y .geojson
        Agrega campo MIN_DIST para visualizar etiquetas. """
    df = add_min_dist(df)
    df.to_csv(saliomapita_dependency.CSV_TEMPLATE.format(df_name),index=False)
    save_restricted_map(info_gdf.GLOBAL_INFO_GDF, df, saliomapita_dependency.GEOJSON_TEMPLATE.format(df_name))

def construct_tables():
    print('Generating argentinian time series...')
    ts_arg = time_series.time_series_arg()
    print('Generating countries time series...')
    ts_countries = time_series.time_series_countries()

    print('Generating images')
    visualization_tools.calculate_images(ts_arg)
    visualization_tools.calculate_images(ts_countries)

    print('Generating final view tables...')
    df_arg       = final_view(ts_arg)
    df_arg       = pd.merge(df_arg,  info_df.GLOBAL_INFO_DF['LOCATION'],on='LOCATION',how='outer').fillna(0)

    df_countries = final_view(ts_countries)

    df_provinces   = df_arg[df_arg['LOCATION'].apply(lambda l : l.count('/')==1)]
    df_departments = df_arg[df_arg['LOCATION'].apply(lambda l : l.count('/')==2)]

    print('Saving provinces...')
    save_final_view(df_provinces, 'provinces')
    print('Saving departments...')
    save_final_view(df_departments, 'departments')
    print('Saving countries...')
    save_final_view(df_countries, 'countries')

if __name__ == '__main__':
    #download.download_csvs()
    construct_tables()
