import pandas as pd
import numpy as np
import wget
import requests
import re
import os
import tarfile
import chardet
import math
import multiprocessing
import tqdm
import functools
import datetime

DATA_PATH = './data'
def download_all_csvs():
    """ Descarga los reportes nacionales de https://covidstats.com.ar/archivos/  """
    r = requests.get('https://covidstats.com.ar/archivos/')
    all_compressed_csvs = sorted(list(set(re.findall(r'Covid19Casos.2020[0-9]{4}(?:.utf8)?.csv.tgz', r.text))))
    for csv_compressed_fn in all_compressed_csvs:
        wget.download(os.path.join("https://covidstats.com.ar/archivos/",csv_compressed_fn),
                      os.path.join(DATA_PATH, csv_compressed_fn))

def extract_targz(targz_fn, output_dir = DATA_PATH):
    """ Extrae un tgz de targz_fn a output_dir.  """
    tar = tarfile.open(targz_fn, "r:gz")
    tar.extractall(output_dir)
    tar.close()

def extract_all_tar():
    """ Extrae todos los tgx de DATA_PATH """
    all_data_files = [ os.path.join(DATA_PATH,tar_fn) for tar_fn in sorted(os.listdir(DATA_PATH)) ]
    all_targz_sorted = [ tar_fp for tar_fp in all_data_files if os.path.isfile(tar_fp) and tar_fp.endswith('.tgz') ]
    p = multiprocessing.Pool(8)
    list(tqdm.tqdm(p.imap(extract_targz, all_targz_sorted),total=len(all_targz_sorted)))

def open_any_encoding(csv_fp):
    """ Abre cualquier csv detectando el encoding. """
    with open(csv_fp, 'rb') as f:
        result = chardet.detect(b''.join(f.readlines(1000000)))
    return pd.read_csv(csv_fp,encoding=result['encoding'])

def filter_confirmados(df):
    return df[df['clasificacion_resumen']=='Confirmado'].copy()

def filter_confirmados_con_fis(df):
    return df[ (df['clasificacion_resumen']=='Confirmado') & (~df['fecha_inicio_sintomas'].isna())].copy()

def filter_uci(df):
    return df[(df['cuidado_intensivo']=='SI') & (df['clasificacion_resumen']=='Confirmado')]

def filter_fallecidos(df):
    return df[(~df['fecha_fallecimiento'].isna()) & (df['clasificacion_resumen']=='Confirmado')].copy()

def group_by_date(date_column, df):
    """ df debe tener las columnas ['LOCATION', date_column, 'id_evento_caso']
        Agrupa los casos por LOCATION y date_column y los cuenta. """
    group_by = ['LOCATION',date_column]
    return df[group_by+['id_evento_caso']].groupby(group_by).count().\
           rename(columns={'id_evento_caso':'value'}).reset_index()

def set_location(hierarchy_location_columns, df):
    """ Crea la columnas LOCATION basandose en las columnas especificadas en
        hierarchy_location_columns en dicho orden de jerarquia.
        Ejemplo: si hierarchy_location_columns = ['provincia_nombre', 'departamento_nombre']
        produciria location como 'ALL/SANTA FE/ROSARIO' """
    df['LOCATION']='ALL'
    for location in hierarchy_location_columns:
        df['LOCATION'] += '/'+df[location]
    return df

def csv_date(csv_fn):
    """ Dado un csv extrae la fecha del mismo. Ejemplo:
        'Covid19Casos.20200616.utf8.csv' -> '2020-06-16'  """
    matches = re.findall(r'2020([0-9]{2})([0-9]{2})',csv_fn)
    assert len(matches)==1
    return '2020-'+matches[0][0]+'-'+matches[0][1]

def create_history_df(csv_oldest_date, analysed_date_column, locations_columns_hierarchy, filter_function, verbose=True):
    """ Tomamos todos los csvs mas recientes que 'csv_oldest_date' y generamos un DataFrame con 3 columnas
        'LOCATION' analysed_date_column 'value' 'fecha_csv'
         Cada fila expresa cuantas entradas tiene el csv de la fecha indicada en 'fecha_csv' para la columna
         de datos analysed_date_column segun la granularidad indicada en la jerarquia locations_columns
         Aplicamos al csv filter_function antes de cualquier calculo.
    """
    all_data_files = [ os.path.join(DATA_PATH,tar_fn) for tar_fn in sorted(os.listdir(DATA_PATH)) ]
    all_csvs_sorted = [ csv_fp for csv_fp in all_data_files if os.path.isfile(csv_fp) and csv_fp.endswith('.csv') ]
    all_dfs = []
    for csv_fp in all_csvs_sorted:
        df_date = csv_date(csv_fp)
        if df_date<csv_oldest_date:
            continue
        if verbose:
            print('Reading {}...'.format(csv_fp))
        df = open_any_encoding(csv_fp)
        df = filter_function(df)
        df = set_location(locations_columns_hierarchy,df)
        df = group_by_date(analysed_date_column,df)
        df['fecha_csv'] = df_date
        all_dfs.append(df)
    return pd.concat(all_dfs, ignore_index=True)

def format_history_df(df, analysed_date_column):
    """ Agrega las columnas:
        - value_diff: para cada analysed_date_column y fecha_csv, cuantos nuevos reportes hay
          para dicha analysed_date_column respecto al informe anterior.
        - delay: cada fila representa una cantidad de personas (value_diff) informada
          en cierto dia (fecha_csv) para cierta fecha analizada (analysed_date_column)
          delay es la cantidad de dias de retraso de la entrada (fecha_csv - analysed_date_column)
        - valuer_ratio: es el % sobre el total actualmente reportado para analysed_date_column
          hasta fecha_csv.
        - weighted_delay: delay ponderado por value_diff para calcular expected_delay. """
    oldest_csv_date = min(df['fecha_csv'])
    df = df[df[analysed_date_column]>=oldest_csv_date].copy()

    to_concat = []
    for name, gdf in df.groupby(['LOCATION',analysed_date_column]):
        location, date = name
        # No tiene sentido que algo sea reportado en un csv con fecha posterior al csv
        # Pero a veces existen errores, aunque no son demasiados
        gdf = gdf[gdf[analysed_date_column]<=gdf['fecha_csv']].copy()

        # Calculamos cuantos se sumaron diariamente a la columna ANALYSED_DATE_COLUMN en esa LOCATION
        gdf = gdf.sort_values('fecha_csv')
        gdf['value_diff'] = gdf['value'].diff()

        # El valor de reportado inicial no se calcula por diferencia
        first_csv_in_group = min(gdf['fecha_csv'])
        gdf.loc[first_csv_in_group==gdf['fecha_csv'],'value_diff'] = gdf['value']

        # Una columna para la cantidad de dias que se esta demorado
        gdf['delay'] = ( pd.to_datetime(gdf['fecha_csv'],format='%Y-%m-%d') -
                         pd.to_datetime(gdf[analysed_date_column],format='%Y-%m-%d'))\
                            .apply(lambda d: d.days)

        # Para calcular el promedio ponterado de la cantidad de dias de espera
        gdf['weighted_delay']=gdf['delay']*gdf['value_diff']

        # Proporcion completado luego del n-esimo dia
        gdf['value_ratio']=gdf['value']/max(gdf['value'])

        to_concat.append(gdf)

    df = pd.concat(to_concat, ignore_index=True)
    df = df.sort_values(['LOCATION',analysed_date_column,'fecha_csv'])
    return df

def history_df_cumulative(df, analysed_date_column):
    """ Dado un dataframe con columnas LOCATION analysed_date_column value, delay
        calcula la misma informacion pero de una perspectiva acumulativa:
        teniendo en cuenta el delay para analysed_date_column o fechas anteriores. """
    to_concat = []
    for location, gdf_location in df.groupby('LOCATION'):
        for date in sorted(list(set(gdf_location[analysed_date_column]))):
            # Filter analysed_date_column <= current_selected_date and sum the value_diff for each delay
            df_filtered = gdf_location[gdf_location[analysed_date_column]<=date].copy()
            df_filtered = df_filtered.groupby('delay')['value_diff'].sum().to_frame().reset_index()
            # Set current location an date
            df_filtered[analysed_date_column]=date
            df_filtered['LOCATION']=location
            to_concat.append(df_filtered)

    cumdf = pd.concat(to_concat,ignore_index=True)
    to_concat = []
    for _,gdf in cumdf.groupby(['LOCATION',analysed_date_column]):
        gdf = gdf.sort_values(['LOCATION',analysed_date_column, 'delay'])
        gdf['value']=gdf['value_diff'].cumsum()
        gdf['value_ratio']=gdf['value']/max(gdf['value'])
        gdf['weighted_delay']=gdf['delay']*gdf['value_diff']
        to_concat.append(gdf)
    cumdf = pd.concat(to_concat,ignore_index=True)
    return cumdf

def expected_delay(df, analysed_date_column):
    """ Cantidad de dias de demora esperada para cada analysed_date_column """
    return (df.groupby(['LOCATION',analysed_date_column])['weighted_delay'].sum()/
        df.groupby(['LOCATION',analysed_date_column])['value_diff'].sum()).rename('expected_delay').to_frame()

def delay_to_confident(df, analysed_date_column, value_ratio_threshold):
    """ Devuelve un DataFrame donde para cada LOCATION, analysed_date_column especifica la cantidad de
        dias (delay) minimo que se necesitaron para alcanzar value_ratio_threshold en value_ratio """
    to_concat = []
    for _,gdf in df.groupby(['LOCATION', analysed_date_column]):
        gdf = gdf[gdf['value_ratio']>=value_ratio_threshold]
        gdf = gdf[gdf['delay']==min(gdf['delay'])]
        to_concat.append(gdf)
    return pd.concat(to_concat,ignore_index=True)[['LOCATION', analysed_date_column, 'delay']]

def delay_indicator(chdf, analysed_date_column):
    """ Para cada LOCATION calcula el indicador explicado en el informe.
        Devuelve la delay indicado y la ultima analysed_date_column que se considero confiable para calcular el delay. """
    last_csv_used = pd.to_datetime(max(chdf[analysed_date_column]),format='%Y-%m-%d')
    percentiles_95 = delay_to_confident(chdf,analysed_date_column,0.95)
    fist_non_valid_by_location = dict()
    for location, gdf in percentiles_95.groupby('LOCATION'):
        gdf_filtered = gdf.copy()
        gdf_filtered['dias_hast_actualidad'] = (last_csv_used -\
            pd.to_datetime(gdf[analysed_date_column], format='%Y-%m-%d')).apply(lambda d: d.days)
        gdf_filtered = gdf_filtered[ gdf_filtered['dias_hast_actualidad'] < gdf['delay'] ]
        if gdf_filtered.empty:
            #print(location)
            #display(gdf_filtered)
            #display(gdf)
            fist_non_valid_by_location[location] = (last_csv_used + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            fist_non_valid_by_location[location] = min(gdf_filtered[analysed_date_column])

    percentiles_90 = delay_to_confident(chdf,analysed_date_column,0.90)
    to_concat = []
    for location, gdf in percentiles_90.groupby('LOCATION'):
        gdf = gdf[gdf[analysed_date_column]<fist_non_valid_by_location[location]]
        gdf = gdf[gdf[analysed_date_column]==max(gdf[analysed_date_column])]
        to_concat.append(gdf)
    return pd.concat(to_concat,ignore_index=True)
