import pandas as pd
import numpy as np
import os
import math
import geopandas as gpd
from shapely.geometry import Point

def which_polygon(gdf, long, lat):
    return gdf[gdf['geometry'].apply(lambda polygon : Point(long,lat).within(polygon))]

def fill_barrios(csv_casos, lat_column, long_column, non_priave_column):
    gdf = gpd.read_file('barrios_rosario.gml')
    df = pd.read_csv(csv_casos)
    df['gml_id'] = df.apply(lambda r: which_polygon(gdf,r[long_column],r[lat_column]).iloc[0]['gml_id'], axis=1)
    df['barrio'] = df.apply(lambda r: which_polygon(gdf,r[long_column],r[lat_column]).iloc[0]['BARRIO'], axis=1)
    df = df[ non_priave_column + ['gml_id','barrio'] ]
    return df

"""
Lee el csv CSV_FILENAME_IN que debe tener una fila por caso. Le coloca una columna con el id y nombre del
barrio (gml_id y barrio respectivamente). Se queda con las columnas NON_PRIVATE_COLUMNS (para no filtrar
informacion privada) y genera CSV_FILENAME_OUT con el resultado.
La info por barrio se saca de 'barrios_rosario.gml'

Configurar cambiando estas constantes:
"""
LONG_COLUMN = 'long'
LAT_COLUMN = 'lat'
NON_PRIVATE_COLUMNS = ['estado','fecha_diagnostico','fecha_fallecimiento']
CSV_FILENAME_IN = './casos.csv'
CSV_FILENAME_OUT = './casos_out.csv'

fill_barrios(CSV_FILENAME_IN, LAT_COLUMN, LONG_COLUMN, NON_PRIVATE_COLUMNS).to_csv(CSV_FILENAME_OUT,index=False)
