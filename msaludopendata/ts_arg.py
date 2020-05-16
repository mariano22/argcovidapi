import pandas as pd
import numpy as np
import os
import datetime
from common import *

def correct_date(date):
    date_format = '%Y-%m-%d'
    if type(date)==str:
        return pd.to_datetime(date,format=date_format).replace(year=2020).strftime(DATE_FORMAT)
    return date

def get_data_cleared():
    df = pd.read_csv(DATA_IN_CSV_CASOS_ARG)
    cols = [
        'provincia_residencia',
        'departamento_residencia',
        'fecha_fis',
        'fallecido',
        'fecha_fallecimiento',
        'clasificacion_resumen'
    ]
    df = df[cols]
    df['fecha_fis']=df['fecha_fis'].apply(correct_date)
    df['fecha_fallecimiento']=df['fecha_fallecimiento'].apply(correct_date)
    df['provincia_residencia']=df['provincia_residencia'].apply(normalize_str)
    df['departamento_residencia']=df['departamento_residencia'].apply(normalize_str)
    df['LOCATION']='ARGENTINA/'+df['provincia_residencia']+'/'+df['departamento_residencia']
    location_replace_dict = {
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

def confirmados_df(df):
    df_confirmados = df[df['clasificacion_resumen']=='Confirmado'].copy()
    df_confirmados = df_confirmados[['LOCATION', 'fecha_fis']].rename(columns={'fecha_fis':'date'})
    df_confirmados = pivot_time_series(df_confirmados)
    df_confirmados = correct_time_series(df_confirmados)
    return df_confirmados

def fallecidos_df(df):
    df_fallecidos = df[(~df['fecha_fallecimiento'].isna()) & (df['clasificacion_resumen']=='Confirmado')].copy()
    df_fallecidos = df_fallecidos[['LOCATION', 'fecha_fallecimiento']].rename(columns={'fecha_fallecimiento':'date'})
    df_fallecidos = pivot_time_series(df_fallecidos)
    df_fallecidos = correct_time_series(df_fallecidos)
    return df_fallecidos

def construct_time_series(df):
    df_confirmados = confirmados_df(df).reset_index()
    df_confirmados['TYPE']='CONFIRMADOS'
    df_fallecidos = fallecidos_df(df).reset_index()
    df_fallecidos['TYPE']='MUERTOS'
    df_result = pd.concat([df_confirmados, df_fallecidos],ignore_index=True).set_index(['TYPE', 'LOCATION'])
    df_result = correct_time_series(df_result)
    return df_result

def ts_arg():
    df_cases = get_data_cleared()
    assert all(df_cases['LOCATION'].apply(lambda l : l.count('/')==2))
    df_deps = construct_time_series(df_cases)
    df_cases_provs = df_cases.copy()
    df_cases_provs['LOCATION'] = df_cases_provs['LOCATION'].apply(lambda l : os.path.dirname(l))
    assert all(df_cases_provs['LOCATION'].apply(lambda l : l.count('/')==1))
    df_provs = construct_time_series(df_cases_provs)

    df = pd.concat([df_deps,df_provs])
    df = df.cumsum(axis=1)
    return df

if __name__ == '__main__':
    ts_arg().to_csv('../csvs/Argentina_time_series.csv')
