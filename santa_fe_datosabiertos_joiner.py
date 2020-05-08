import pandas as pd
import numpy as np
import os
from bs4 import BeautifulSoup, SoupStrainer
import requests, zipfile, io

import santa_fe_api
from common import *

SANTA_FE_DATOSABIERTOS_URL = "https://www.santafe.gob.ar/ms/covid19/datosabiertos/"
DOWNLOAD_DIR = 'santa_fe_download/'
LOCALIDAD_TO_DEPARTAMENTO_FILENAME = 'santa_fe_departamento_localidad.csv'
NOTIFICACIONES_LOCALIDAD_FILENAME = 'notificaciones_localidad.csv'
REPO_DATA_FILENAME = 'csvs/SantaFe_AllData.csv'

def read_datosabiertos(last_date):
    # Read info table to complete departments
    df_info = pd.read_csv(os.path.join(DOWNLOAD_DIR,LOCALIDAD_TO_DEPARTAMENTO_FILENAME))
    df_info['DEPARTMENT']=df_info['Departamento'].apply(normalize_str)
    df_info['PLACE']=df_info['Localidad'].apply(normalize_str)

    # Read historical data by city
    df = pd.read_csv(os.path.join(DOWNLOAD_DIR,NOTIFICACIONES_LOCALIDAD_FILENAME))
    df = df.rename(columns = {'localidad': 'PLACE',
                              'Confirmados': 'CONFIRMADOS',
                              'Descartados': 'DESCARTADOS',
                              'En estudio': 'SOSPECHOSOS',
                              'Notificaciones': 'NOTIFICACIONES',
                                })
    # Add department field
    df['PLACE']=df['PLACE'].apply(normalize_str)
    df = pd.merge(df,df_info[['PLACE','DEPARTMENT']],on='PLACE',how='left')
    df['DEPARTMENT'] = '#D_'+df['DEPARTMENT']

    # Shape with as API dataframe (TYPE, DEPARTMENT, PLACE as index, DATE as columns)
    type_cols = ['CONFIRMADOS', 'DESCARTADOS', 'SOSPECHOSOS', 'NOTIFICACIONES']
    df = pd.melt(df, id_vars=['DEPARTMENT','PLACE','Fecha'], value_vars=type_cols,var_name='TYPE', value_name='value')
    df['Fecha'] = df['Fecha'].apply(lambda date : pd.to_datetime(date,format='%Y-%m-%d'))
    df = df.pivot_table(index=['TYPE','DEPARTMENT','PLACE'], columns='Fecha', values='value')
    df = df.fillna(0)

    # Filter data before MIGRATION_DATE
    last_date = pd.to_datetime(last_date,format='%d/%m/%Y')
    df = df[[c for c in df.columns if last_date < c]]
    df = df.rename(columns=lambda date: date.strftime('%d/%m/%Y'))

    # Complete total functions
    df = santa_fe_api.complete_deparments_and_total(df)
    return df


def _santa_fe_zip_download():
    page = requests.get(SANTA_FE_DATOSABIERTOS_URL)
    data = page.text
    soup = BeautifulSoup(data,features='lxml')

    match_url = []
    for link in soup.find_all('a'):
        url = link.get('href')
        if url.endswith('zip'):
            match_url.append(url)
    assert len(match_url)==1
    zip_url = match_url[0]
    r = requests.get(zip_url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(DOWNLOAD_DIR)

def update_santa_fe():
    _santa_fe_zip_download()
    # Read repo data
    df_api = santa_fe_api.SantaFeAPI('./', mock_drive=REPO_DATA_FILENAME).df
    # Read from Santa Fe datos abiertos
    df_new=read_datosabiertos(df_api.columns[-1]).reset_index()
    df_new=santa_fe_api.SantaFeAPI('./', mock_drive=df_new).df
    # Merge dataframes
    df_result = pd.merge(df_api,df_new,left_index=True,right_index=True,how='outer').fillna(0)

    # ASSERT that we just 'paste' the dataframes and did not modify them
    n_already_existing_columns = len(df_api.columns)

    df_result_restricted = df_result[df_result.index.map(lambda i : i in df_api.index)].copy()
    assert all(df_api==df_result_restricted[df_result_restricted.columns[:n_already_existing_columns]])

    df_result_restricted = df_result[df_result.index.map(lambda i : i in df_new.index)].copy()
    assert all(df_new==df_result_restricted[df_result_restricted.columns[n_already_existing_columns:]])

    # Overwrite repo data
    df_result.to_csv(REPO_DATA_FILENAME)

if __name__ == '__main__':
    update_santa_fe()
    touch_timestamp()
