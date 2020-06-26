"""
Genera variable global GLOBAL_INFO_GDF con geopandas con info geográfica (polígonos)
de todas las LOCATION (paises, provs args, deps)
"""
import pandas as pd
import geopandas as gpd

from common import *

GLOBAL_INFO_GDF = None

def info_gdf():
    global GLOBAL_INFO_GDF
    gdf=gpd.read_file(DATA_IN_GEOJSON_ARG)

    gdf_countries = gpd.read_file(DATA_IN_GEOJSON_WORLD)
    gdf_countries['LOCATION']=gdf_countries['ISO_A3'].apply(normalize_str)
    gdf_countries = gdf_countries[gdf_countries['LOCATION']!='-99']
    gdf_countries=gdf_countries[['LOCATION','geometry']]

    GLOBAL_INFO_GDF = gpd.GeoDataFrame( pd.concat([gdf, gdf_countries], ignore_index=True) )
    GLOBAL_INFO_GDF = GLOBAL_INFO_GDF[~GLOBAL_INFO_GDF.duplicated(subset='LOCATION',keep='first')]

info_gdf()
