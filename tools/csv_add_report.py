import os
import pandas as pd
import numpy as np

import sys
sys.path.append('..')
from common import *
import santa_fe_api

def _to_department_dict(places):
    """ Return Dict[place_name, department_name] deducing by the order of given list. """
    to_department = dict()
    curr_department = ''
    for place_name in places:
        if place_name == '##TOTAL':
            to_department[place_name] = '##TOTAL'
        else:
            if santa_fe_api.is_deparment(place_name):
                curr_department = place_name
            to_department[place_name] = curr_department
    return to_department

def _add_department_index(df):
    """ Given a DataFrame which index is place, add department index. """
    df['DEPARTMENT'] = df.index
    to_department = _to_department_dict(df.index)
    df['DEPARTMENT'] = df['DEPARTMENT'].apply(lambda x : to_department[x])
    df = df.set_index('DEPARTMENT',append=True)
    return df

def _process_last_update(df,current_date):
    """ Process a parsed report update to satisfy the format of API """
    df = df.rename(columns = {'Departamento/ Localidad': 'PLACE',
                          'Confirmados': 'CONFIRMADOS',
                          'Descartados': 'DESCARTADOS',
                          'Sospechosos': 'SOSPECHOSOS',
                            })
    df = pd.melt(df, id_vars=['PLACE'], value_vars=['CONFIRMADOS', 'DESCARTADOS', 'SOSPECHOSOS'],\
                 var_name='TYPE', value_name=current_date)
    df = df.set_index('PLACE')
    df = _add_department_index(df)
    df = df.set_index('TYPE',append=True)

    df = df.reorder_levels(['TYPE','DEPARTMENT','PLACE'])
    df = df.sort_index()
    return df

def join_report_data(base_api_csv, report_date, report_csv):
    """ Join the data on API with a new report. """
    # Get the data acumulated on API
    apisafe = santa_fe_api.SantaFeAPI('./', mock_drive=base_api_csv)
    # Read and process last report
    df_last = pd.read_csv(report_csv)
    df_last = _process_last_update(df_last,report_date)
    # Concat by column and returns
    return pd.concat([apisafe.df,df_last],axis=1).fillna(0)
