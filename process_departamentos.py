import pandas as pd
import numpy as np
import os

from common import *

def correct_time_series(df):
    for index, row in df.iterrows():
        new_row_data = [0]
        for _, value in row.iteritems():
            if value>0:
                new_row_data.append(value)
            else:
                new_row_data.append(new_row_data[-1])
        df.loc[index]=pd.Series(new_row_data[1:],index=row.index)
    return df

def process_department(csv_filename, type_cols, date_format, provincia, df_info,dep_replacing=None):
    df = pd.read_csv(csv_filename)
    df['DEPARTMENTO']=df['DEPARTMENTO'].apply(normalize_str)
    if dep_replacing is not None:
        df['DEPARTMENTO']=df['DEPARTMENTO'].apply(dep_replacing)
    df['LOCALIDAD']=df['LOCALIDAD'].apply(normalize_str)
    df['DATE'] = df['DATE'].apply(lambda date : pd.to_datetime(date,format=date_format))

    df = pd.melt(df, id_vars=['DEPARTMENTO','LOCALIDAD','DATE'], value_vars=type_cols,var_name='TYPE', value_name='value')
    df = df.pivot_table(index=['TYPE','DEPARTMENTO','LOCALIDAD'], columns='DATE', values='value')
    df = correct_time_series(df)
    df = df.rename(columns=lambda date: date.strftime('%d/%m/%Y'))
    df = df.reset_index()

    df_departments = df.groupby(['TYPE','DEPARTMENTO']).sum().reset_index()
    df_departments['LOCATION'] = 'ARGENTINA/' + provincia + '/' + df_departments['DEPARTMENTO']
    df_departments = df_departments.set_index(['TYPE','LOCATION'])
    df_departments = df_departments.drop(columns=['DEPARTMENTO'])


    df['LOCATION'] = 'ARGENTINA/' + provincia + '/' + df['DEPARTMENTO'] + '/'+df['LOCALIDAD']
    df = df.set_index(['TYPE','LOCATION'])
    df = df.drop(columns=['LOCALIDAD','DEPARTMENTO'])

    df = pd.concat([df,df_departments]).sort_index()

    location_set = set(df_info['LOCATION'])
    for location in df.index.get_level_values(1):
        if location not in location_set and location.count('/')==2:
            print(location)
    return df


def dep_replacing_cordoba(department):
    if 'ROCA' in department and 'GRAL' in department:
        return 'GENERAL ROCA'
    if 'SAN MARTIN' in department and 'GRAL' in department:
        return 'GENERAL SAN MARTIN'
    if 'SAENZ PENA' in department:
        return 'PRESIDENTE ROQUE SAENZ PENA'
    if 'CAPITAL' in department:
        return 'CAPITAL'
    return department


if __name__ == '__main__':
    df_cordoba = process_department(csv_filename = 'cordoba.csv',
                                    type_cols = ['CONFIRMADOS'],
                                    date_format = '%d/%m/%Y',
                                    provincia = 'CORDOBA',
                                    df_info = pd.read_csv('info_general.csv'),
                                    dep_replacing = dep_replacing_cordoba)
    df_cordoba.to_csv('csvs/Cordoba_AllData.csv')
    # Overwrite repo data
    touch_timestamp()
