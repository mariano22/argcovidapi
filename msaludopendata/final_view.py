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
import partidos_amba

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
    arg_ts = time_series.time_series_arg()
    print('Generating countries time series...')
    countries_ts = time_series.time_series_countries()
    print('Generating caba time series...')
    caba_ts = time_series.time_series_caba()

    # Set Argentina row in ts_countries using MinSalud data (instead of JohnHopkins global data)
    countries_ts = countries_ts.reset_index()
    arg_ts       = arg_ts.reset_index()
    only_arg_ts  = arg_ts[arg_ts['LOCATION']=='ARG']
    arg_ts       = arg_ts[arg_ts['LOCATION']!='ARG']
    countries_ts = countries_ts[countries_ts['LOCATION']!='ARG']
    only_arg_ts = only_arg_ts.set_index(['TYPE', 'LOCATION']).sort_index()
    countries_ts = countries_ts.set_index(['TYPE', 'LOCATION']).sort_index()
    arg_ts       = arg_ts.set_index(['TYPE', 'LOCATION']).sort_index()
    countries_ts = concat_time_series([countries_ts,only_arg_ts])

    print('Generating time series')
    all_ts = concat_time_series([countries_ts,arg_ts,caba_ts])
    types = ['CONFIRMADOS','CONFIRMADOS_PER100K',
             'MUERTOS', 'MUERTOS_PER100K',
            ]
    all_ts = all_ts[all_ts.index.map(lambda l : l[0] in types)]
    all_ts=all_ts[all_ts.columns[-70:]]
    all_ts_melted = pd.melt(all_ts.reset_index(), id_vars=['TYPE','LOCATION'], value_vars=all_ts.columns, var_name='date')
    all_ts_melted.to_csv(saliomapita_dependency.CSV_TIME_SERIES,index=False)

    print('Generating images')
    visualization_tools.calculate_images(arg_ts)
    visualization_tools.calculate_images(countries_ts)
    visualization_tools.calculate_images(caba_ts)

    print('Generating final view tables...')
    df_arg       = final_view(arg_ts)
    df_arg       = pd.merge(df_arg,  info_df.GLOBAL_INFO_DF['LOCATION'],on='LOCATION',how='outer').fillna(0)

    df_countries = final_view(countries_ts)
    df_caba      = final_view(caba_ts)

    df_provinces   = df_arg[df_arg['LOCATION'].apply(lambda l : l.count('/')==1)]
    df_departments = df_arg[df_arg['LOCATION'].apply(lambda l : l.count('/')==2)]

    df_partidos_amba = df_departments[
        df_departments['LOCATION'].apply(lambda l : l in partidos_amba.partidos_amba)]
    df_amba = pd.concat([df_caba,df_partidos_amba],ignore_index=True)

    print('Saving provinces...')
    save_final_view(df_provinces, 'provinces')
    print('Saving departments...')
    save_final_view(df_departments, 'departments')
    print('Saving countries...')
    save_final_view(df_countries, 'countries')
    print('Saving caba...')
    save_final_view(df_amba, 'caba')

if __name__ == '__main__':
    download.download_csvs()
    construct_tables()
