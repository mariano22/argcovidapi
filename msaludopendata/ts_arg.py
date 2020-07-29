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

""" Algunas definiciones de nombres de columnas para la tabla CovidCasos de MinSalud. """
FECHA_FIS = 'fecha_diagnostico'
FECHA_CUIDADO_INTENSIVO = 'fecha_cui_intensivo'
PROVINCIA_RESIDENCIA = 'residencia_provincia_nombre'
DEPARTAMENTO_RESIDENCIA = 'residencia_departamento_nombre'
CLASIFICACION = 'clasificacion'

def correct_date(date):
    """ Set year=2020 Some cases appear with bad year on date. """
    date_format = '%Y-%m-%d'
    if type(date)==str:
        date = '2020'+date[4:]
        return pd.to_datetime(date,format=date_format).replace(year=2020).strftime(DATE_FORMAT)
    return date

def comuna_lzero(department_str):
    if department_str.startswith('COMUNA 0'):
        return 'COMUNA '+department_str[len('COMUNA 0'):]
    return department_str

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
        CLASIFICACION,
        'cuidado_intensivo',
        FECHA_CUIDADO_INTENSIVO,
        'carga_provincia_nombre'
    ]
    df = df[cols]

    df[PROVINCIA_RESIDENCIA]=df[PROVINCIA_RESIDENCIA].apply(normalize_str)
    df[DEPARTAMENTO_RESIDENCIA]=df[DEPARTAMENTO_RESIDENCIA].apply(normalize_str)
    df['carga_provincia_nombre']=df['carga_provincia_nombre'].apply(normalize_str)
    df[CLASIFICACION]=df[CLASIFICACION].apply(normalize_str)


    df[FECHA_FIS]=df[FECHA_FIS].apply(correct_date)
    df.loc[(df[PROVINCIA_RESIDENCIA]=='SIN ESPECIFICAR'),PROVINCIA_RESIDENCIA] =  df['carga_provincia_nombre']
    df.loc[(df['fallecido']=='SI') & df['fecha_fallecimiento'].isna(),'fecha_fallecimiento'] =  df[FECHA_FIS]
    df.loc[(df['fallecido']=='SI') & df[FECHA_FIS].isna(),FECHA_FIS] =  df['fecha_fallecimiento']
    df.loc[(df['cuidado_intensivo']=='SI') & df[FECHA_CUIDADO_INTENSIVO].isna(),FECHA_CUIDADO_INTENSIVO] = df[FECHA_FIS]
    df['fecha_fallecimiento']=df['fecha_fallecimiento'].apply(correct_date)
    df[FECHA_CUIDADO_INTENSIVO]=df[FECHA_CUIDADO_INTENSIVO].apply(correct_date)
    df[DEPARTAMENTO_RESIDENCIA]=df[DEPARTAMENTO_RESIDENCIA].apply(comuna_lzero)
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
    """ Dada tabla con columnas {'LOCATION', 'date'} construye una serie temporal
        no acumulativa. O sea, con indice LOCATION, columnas las diferentes
        fechas que aparecen y valor la cantidad de entradas que caen en dicha fecha. """
    df['value']=1
    df = df.groupby(['LOCATION','date']).sum().reset_index()
    df = df.pivot_table(index=['LOCATION'], columns='date', values='value')
    df = df.fillna(0)
    return df

def build_ts(df, date_column):
    """ Tabla de casos (una fila, un caso) con columnas LOCATION y date_column
        construye una serie temporal acumulativa en base a date_column. """
    df = df[['LOCATION', date_column]].rename(columns={date_column:'date'})
    assert set(df.columns)=={'LOCATION', 'date'}
    ts = pivot_time_series(df)
    # Esto calcula los acumulados
    ts = ts.cumsum(axis=1)
    ts = correct_ts(ts)
    return ts

def repartir_sin_especificar(ts):
    """ Dada una serie temporal con indice LOCATION reparte las entradas SIN ESPECIFICAR
        entre las que compartan el mismo PARENT_LOCATION (os.path.dirname(LOCATION))
        lo hace proporcionalmente y redondeando. """
    # Filtramos quedandonos con los que no terminan en 'SIN ESPECIFICAR'
    ts_especificado =  ts[ts.index.map(lambda l : 'SIN ESPECIFICAR' not in l)].copy()

    # Calculamos el total agrupando por 'PARENT_LOCATION' (os.path.dirname(LOCATION)) una vez aplicado el filtro
    ts_total_especificado = ts_especificado.copy()
    ts_total_especificado.index = ts_total_especificado.index.map(os.path.dirname)
    ts_total_especificado = ts_total_especificado.reset_index().groupby('LOCATION').sum()

    # Filtramos los que terminan en 'NO ESPECIFIAR', los indexamos por PARENT_LOCATION
    ts_sin_especificar = ts[ts.index.map(lambda l : 'SIN ESPECIFICAR' in l)].copy()
    ts_sin_especificar.index = ts_sin_especificar.index.map(os.path.dirname)
    # Agregamos 0's a los PARENT_LOCATION que figuran en ts_especificado pero NO poseen SIN ESPECIFICAR (SIN ESPECIFICAR = 0 para esos casos)
    ts_sin_especificar = ts_sin_especificar.append(
        pd.DataFrame(index = set(l for l in ts_especificado.index.map(os.path.dirname) if l not in ts_sin_especificar.index),
                     columns = ts_sin_especificar.columns).fillna(0))

    # Creamos DataFrame del mismo shape que ts_especificado con los ts_sin_especificar y ts_total_especificado
    # respectivo al PARENT_LOCATION de cada ts_especificado.
    ts_sin_especificar_respectivo = ts_sin_especificar.loc[ts_especificado.index.map(os.path.dirname)].copy()
    ts_sin_especificar_respectivo.index = ts_especificado.index

    ts_total_respectivo = ts_total_especificado.loc[ts_especificado.index.map(os.path.dirname)].copy()
    ts_total_respectivo.index = ts_especificado.index

    return round(ts_especificado + (ts_especificado/ts_total_respectivo).fillna(0) * ts_sin_especificar_respectivo)

def uci_df(df):
    """ Tabla de casos -> serie temporal de UCI (pacientes en terapia intensiva) por LOCATION """
    df_uci = df[(df['cuidado_intensivo']=='SI') & (df['clasificacion_resumen']=='Confirmado')]
    return build_ts(df_uci, FECHA_CUIDADO_INTENSIVO)

def activos_df(df):
    """ Tabla de casos -> serie temporal de ACTIVOS por LOCATION """
    df_activos = df[df[CLASIFICACION].apply(lambda l: 'ACTIVO' in l and 'NO ACTIVO' not in l)].copy()
    return build_ts(df_activos, FECHA_FIS)

def confirmados_df(df):
    """ Tabla de casos -> serie temporal de CONFIRMADOS por LOCATION """
    df_confirmados = df[df['clasificacion_resumen']=='Confirmado'].copy()
    return build_ts(df_confirmados, FECHA_FIS)

def fallecidos_df(df):
    """ Tabla de casos -> serie temporal de MUERTOS por LOCATION """
    df_fallecidos = df[(~df['fecha_fallecimiento'].isna()) & (df['clasificacion_resumen']=='Confirmado')].copy()
    return build_ts(df_fallecidos, 'fecha_fallecimiento')

def construct_time_series(df):
    """
    Dada una tabla de casos (una fila por caso) construye series temporales de
    cada LOCATION (indice TYPE, LOCATION).
    """
    type_and_ts = [ ('CONFIRMADOS', confirmados_df(df)),
                    ('MUERTOS',     fallecidos_df(df)),
                    ('UCI',         uci_df(df)),
                    ('ACTIVOS',     activos_df(df)),
                  ]
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
    # Tabla de casos con LOCATION por departamento
    df_cases = get_data_cleared()
    assert all(df_cases['LOCATION'].apply(lambda l : l.count('/')==2))

    # Tabla de casos con LOCATION por provincia
    df_cases_provs = df_cases.copy()
    df_cases_provs['LOCATION'] = df_cases_provs['LOCATION'].apply(lambda l : os.path.dirname(l))
    assert all(df_cases_provs['LOCATION'].apply(lambda l : l.count('/')==1))

    # Tabla de casos con LOCATION=='ARG'
    df_cases_arg = df_cases.copy()
    df_cases_arg['LOCATION'] = 'ARG'

    # Contruimos series temporales dada la tabla de casos
    df_deps = construct_time_series(df_cases)
    df_provs = construct_time_series(df_cases_provs)
    df_arg = construct_time_series(df_cases_arg)

    df = concat_time_series([df_deps,df_provs,df_arg])
    return df

if __name__ == '__main__':
    ts_arg().to_csv('../csvs/Argentina_time_series.csv')
