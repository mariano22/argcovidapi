"""
Produce la serie temporal (acumulada) de CABA.
Output functions: ts_caba
"""
import pandas as pd
import numpy as np
import os
import datetime
import chardet
import calendar

from common import *
import ts_arg
import info_df

""" Algunas definiciones de nombres de columnas para la tabla casos_covid19_caba de CABA. """
FECHA_DE_CLASIFICACION = 'fecha_clasificacion'
FECHA_DE_FALLECIMIENTO = 'fecha_fallecimiento'
CLASIFICACION = 'clasificacion'
PROVINCIA = 'provincia'
BARRIO = 'barrio'
COMUNA = 'comuna'

"""
# DEPRECATED: Esto estaba porque la fecha antes tenia un formato raro
MONTH_ABRR_TO_NUMBER = {v.upper(): k for k,v in enumerate(calendar.month_abbr)}
def caba_date_to_iso(date):
    # Transforma la fecha de los informes de caba formato 20APR2020:00:00:00.000000 a DATE_FORMAT
    global month_abrr_to_number
    if type(date)==float:
        assert math.isnan(date)
        return date
    data_str = '2020-{}-{}'.format(MONTH_ABRR_TO_NUMBER[date[2:5]],date[0:2])
    return pd.to_datetime(data_str,format=DATE_FORMAT)
"""

def process_barrio(barrio):
    """ Normaliza el barrio agregando SIN ESPECIFIAR donde corresponda """
    global month_abrr_to_number
    if type(barrio)==float:
        assert math.isnan(barrio)
        return 'SIN ESPECIFICAR'
    return normalize_str(barrio)

def get_data_cleared():
    """ Produce la tabla donde cada fila es un caso, hace algunas correcciones. """
    with open(DATA_IN_CSV_CASOS_CABA, 'rb') as f:
        result = chardet.detect(b''.join(f.readlines()))
    df = pd.read_csv(DATA_IN_CSV_CASOS_CABA,encoding=result['encoding'])

    df=df[df[PROVINCIA]=='CABA']
    df[FECHA_DE_CLASIFICACION] = df[FECHA_DE_CLASIFICACION].apply(ts_arg.correct_date)
    df[FECHA_DE_FALLECIMIENTO] = df[FECHA_DE_FALLECIMIENTO].apply(ts_arg.correct_date)

    df[PROVINCIA]=df[PROVINCIA].apply(normalize_str)
    df[BARRIO]=df[BARRIO].apply(process_barrio)
    df[CLASIFICACION]=df[CLASIFICACION].apply(normalize_str)
    df[COMUNA]=df[COMUNA].apply(lambda x : 'SIN ESPECIFICAR' if math.isnan(x) else 'COMUNA '+str(int(x)))
    # Los que no tienen barrio -> no tienen comuna especificada
    assert df[~df[COMUNA].isna() & df[BARRIO].isna()].empty

    df['LOCATION']='ARGENTINA/CABA/'+df[BARRIO]
    return df

def confirmados_df(df):
    """ Tabla de casos -> serie temporal de CONFIRMADOS por LOCATION """
    df_confirmados = df[(df[CLASIFICACION]=='CONFIRMADO') | (df[CLASIFICACION]=='NEGATIVIZADO')].copy()
    return ts_arg.build_ts(df_confirmados,FECHA_DE_CLASIFICACION)

def fallecidos_df(df):
    """ Tabla de casos -> serie temporal de MUERTOS por LOCATION """
    df_fallecidos = df[(~df[FECHA_DE_FALLECIMIENTO].isna()) & (df[CLASIFICACION]=='CONFIRMADO')].copy()
    return ts_arg.build_ts(df_fallecidos, FECHA_DE_FALLECIMIENTO)

def repartir_sin_especificar(ts):
    """ Reparte los casos sin especificar granularidad (ARGENTINA/CABA/SIN ESPECIFIAR) proporcionalmente por barrio """
    sin_especificar_index = ts.index.map(lambda l : 'SIN ESPECIFICAR' in l)
    ts_sin_especificar = ts[sin_especificar_index].loc['ARGENTINA/CABA/SIN ESPECIFICAR']
    ts_especificado = ts[sin_especificar_index.map(lambda x : not(x))]
    return round( ts_especificado + (ts_especificado/ts_especificado.sum()).fillna(0) * ts_sin_especificar )

def construct_time_series(df):
    """
    Dada una tabla de casos (una fila por caso) construye series temporales de
    cada LOCATION (indice TYPE, LOCATION).
    """
    type_and_ts = [ ('CONFIRMADOS', confirmados_df(df)),
                    ('MUERTOS',     fallecidos_df(df)) ]
    to_concat = []
    for type, ts in type_and_ts:
        ts=repartir_sin_especificar(ts)
        ts=ts.reset_index()
        ts['TYPE']=type
        ts=ts.set_index(['TYPE', 'LOCATION'])
        to_concat.append(ts)
    df_result = concat_time_series(to_concat)
    return df_result

def fill_comuna(location):
    barrio = os.path.basename(location)
    return 'ARGENTINA/CABA/'+info_df.GLOBAL_BARRIOS_TO_COMUNA[barrio]+'/'+barrio

def ts_caba():
    df_cases = get_data_cleared()
    assert all(df_cases['LOCATION'].apply(lambda l : l.count('/')==2))
    ts = construct_time_series(df_cases)
    ts = ts.reset_index()
    ts['LOCATION']=ts['LOCATION'].apply(fill_comuna)
    ts = ts.set_index(['TYPE', 'LOCATION'])
    return ts

if __name__ == '__main__':
    ts_caba().to_csv('../csvs/CABA_time_series.csv')
