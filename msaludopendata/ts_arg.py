"""
Produce la serie temporal (acumulada) de Argentina.
Output functions: ts_arg
"""
import pandas as pd
import numpy as np
import os
import datetime
from common import *
import chardet

FECHA_FIS = 'fecha_diagnostico'
FECHA_CUIDADO_INTENSIVO = 'fecha_cui_intensivo'
PROVINCIA_RESIDENCIA = 'residencia_provincia_nombre'
DEPARTAMENTO_RESIDENCIA = 'residencia_departamento_nombre'

def correct_date(date):
    date_format = '%Y-%m-%d'
    if type(date)==str:
        return pd.to_datetime(date,format=date_format).replace(year=2020).strftime(DATE_FORMAT)
    return date

def get_data_cleared():
    """
    Produce la tabla donde cada fila es un caso. Filtra algunas columnas y hace algunas correcciones.
    """
    # Esto es para detectar el encoding con primeros 1000000 lineas
    with open(DATA_IN_CSV_CASOS_ARG, 'rb') as f:
        result = chardet.detect(b''.join(f.readlines(1000000)))
    df = pd.read_csv(DATA_IN_CSV_CASOS_ARG,encoding=result['encoding'])
    cols = [
        PROVINCIA_RESIDENCIA,
        DEPARTAMENTO_RESIDENCIA,
        FECHA_FIS,
        'fallecido',
        'fecha_fallecimiento',
        'clasificacion_resumen',
        'cuidado_intensivo',
        FECHA_CUIDADO_INTENSIVO,
        'carga_provincia_nombre'
    ]
    df = df[cols]

    df[PROVINCIA_RESIDENCIA]=df[PROVINCIA_RESIDENCIA].apply(normalize_str)
    df[DEPARTAMENTO_RESIDENCIA]=df[DEPARTAMENTO_RESIDENCIA].apply(normalize_str)
    df['carga_provincia_nombre']=df['carga_provincia_nombre'].apply(normalize_str)


    df[FECHA_FIS]=df[FECHA_FIS].apply(correct_date)
    df.loc[(df[PROVINCIA_RESIDENCIA]=='SIN ESPECIFICAR'),PROVINCIA_RESIDENCIA] =  df['carga_provincia_nombre']
    df.loc[(df['fallecido']=='SI') & df['fecha_fallecimiento'].isna(),'fecha_fallecimiento'] =  df[FECHA_FIS]
    df.loc[(df['fallecido']=='SI') & df[FECHA_FIS].isna(),FECHA_FIS] =  df['fecha_fallecimiento']
    df.loc[(df['cuidado_intensivo']=='SI') & df[FECHA_CUIDADO_INTENSIVO].isna(),FECHA_CUIDADO_INTENSIVO] = df[FECHA_FIS]
    df['fecha_fallecimiento']=df['fecha_fallecimiento'].apply(correct_date)
    df[FECHA_CUIDADO_INTENSIVO]=df[FECHA_CUIDADO_INTENSIVO].apply(correct_date)
    df['LOCATION']='ARGENTINA/'+df[PROVINCIA_RESIDENCIA]+'/'+df[DEPARTAMENTO_RESIDENCIA]
    location_replace_dict = {
      'ARGENTINA/SANTIAGO DEL ESTERO/JUAN F. IBARRA': 'ARGENTINA/SANTIAGO DEL ESTERO/JUAN F IBARRA',
      'ARGENTINA/SALTA/GRL. JOSE DE SAN MARTIN': 'ARGENTINA/SALTA/GENERAL JOSE DE SAN MARTIN',
      'ARGENTINA/BUENOS AIRES/CORONEL DE MARINA L. ROSALES':
        'ARGENTINA/BUENOS AIRES/CORONEL DE MARINA LEONARDO ROSALES',
      'ARGENTINA/BUENOS AIRES/JOSE C. PAZ':'ARGENTINA/BUENOS AIRES/JOSE C PAZ',
      'ARGENTINA/BUENOS AIRES/LEANDRO N. ALEM': 'ARGENTINA/BUENOS AIRES/LEANDRO N ALEM',
      'ARGENTINA/CHACO/1O DE MAYO': 'ARGENTINA/CHACO/1 DE MAYO',
      'ARGENTINA/JUJUY/DR. MANUEL BELGRANO': 'ARGENTINA/JUJUY/DOCTOR MANUEL BELGRANO',
      'ARGENTINA/SAN LUIS/LA CAPITAL': 'ARGENTINA/SAN LUIS/JUAN MARTIN DE PUEYRREDON'}
    df['LOCATION']=df['LOCATION'].replace(location_replace_dict)
    return df

def pivot_time_series(df):
    df['value']=1
    df = df.groupby(['LOCATION','date']).sum().reset_index()
    df = df.pivot_table(index=['LOCATION'], columns='date', values='value')
    return df

def build_ts(df, date_column):
    df = df[['LOCATION', date_column]].rename(columns={date_column:'date'})
    assert set(df.columns)=={'LOCATION', 'date'}
    ts = pivot_time_series(df)
    # Esto calcula los acumulados
    ts = ts.fillna(0)
    ts = ts.cumsum(axis=1)
    ts = ts.rename(columns = lambda d : pd.to_datetime(d,format=DATE_FORMAT))
    ts = add_missing_columns(ts)
    ts = correct_time_series(ts)
    check_days_consecutive(ts)
    ts = ts.rename(columns = lambda d : d.strftime(DATE_FORMAT))
    return ts

def uci_df(df):
    df_uci = df[(df['cuidado_intensivo']=='SI') & (df['clasificacion_resumen']=='Confirmado')]
    return build_ts(df_uci, FECHA_CUIDADO_INTENSIVO)

def repartir_sin_especificar(ts):
    ts=ts.reset_index()
    ts['PARENT_LOCATION']=ts['LOCATION'].apply(lambda l : os.path.dirname(l))
    ts_sin_especificar_depto = ts[ts['LOCATION'].apply(lambda l : 'SIN ESPECIFICAR' in l)]
    ts=ts[ts['LOCATION'].apply(lambda l : 'SIN ESPECIFICAR' not in l)]
    ts_sin_especificar_depto=ts_sin_especificar_depto.drop(columns='LOCATION')

    ts_totales=ts.drop(columns='LOCATION').groupby('PARENT_LOCATION').sum()
    ts_sin_especificar_depto=ts_sin_especificar_depto.set_index('PARENT_LOCATION')
    ts = ts.drop(columns='PARENT_LOCATION').set_index('LOCATION')

    hay_sin_especificar_location = set(ts_sin_especificar_depto.index)
    for location, time_serie in ts.iterrows():
        parent_location =  os.path.dirname(location)
        if parent_location in hay_sin_especificar_location:
            ratio = (time_serie/ts_totales.loc[parent_location]).fillna(0)
            diff = round(ratio*ts_sin_especificar_depto.loc[parent_location])
            ts.loc[location] = time_serie + diff
    return ts

def confirmados_df(df):
    df_confirmados = df[df['clasificacion_resumen']=='Confirmado'].copy()
    return build_ts(df_confirmados, FECHA_FIS)

def fallecidos_df(df):
    df_fallecidos = df[(~df['fecha_fallecimiento'].isna()) & (df['clasificacion_resumen']=='Confirmado')].copy()
    return build_ts(df_fallecidos, 'fecha_fallecimiento')

def construct_time_series(df):
    """
    Construye serie temporal por departamento
    """
    type_and_ts = [ ('CONFIRMADOS', confirmados_df(df)),
                    ('MUERTOS', fallecidos_df(df)),
                    ('UCI', uci_df(df)) ]
    to_concat = []
    for type, ts in type_and_ts:
        ts=repartir_sin_especificar(ts)
        ts=ts.reset_index()
        ts['TYPE']=type
        ts=ts.set_index(['TYPE', 'LOCATION'])
        to_concat.append(ts)
    df_result = concat_time_series(to_concat)
    return df_result

def ts_arg():
    # Casos con LOCATION por departamento
    df_cases = get_data_cleared()
    assert all(df_cases['LOCATION'].apply(lambda l : l.count('/')==2))

    # Casos con LOCATION por provincia
    df_cases_provs = df_cases.copy()
    df_cases_provs['LOCATION'] = df_cases_provs['LOCATION'].apply(lambda l : os.path.dirname(l))
    assert all(df_cases_provs['LOCATION'].apply(lambda l : l.count('/')==1))

    df_deps = construct_time_series(df_cases)
    df_provs = construct_time_series(df_cases_provs)

    df = concat_time_series([df_deps,df_provs])
    return df

if __name__ == '__main__':
    ts_arg().to_csv('../csvs/Argentina_time_series.csv')
