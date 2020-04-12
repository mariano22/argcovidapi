import os
import pandas as pd
import numpy as np
from common import *

import santa_fe_api

def _format_department(place_name):
    return ('#' if place_name[:2]=='D_' else '') + place_name

if __name__ == '__main__':
    """ Read the data from format until 09/4/2020 and produce
        'result_migration.csv' with the new format. """
    apisafe = santa_fe_api.SantaFeAPI('./')
    colset = list(apisafe.df_confirmados.columns)
    colset = colset[:colset.index('10/4/2020')]
    apisafe.df_confirmados = apisafe.df_confirmados[colset]
    apisafe.df_descartados = apisafe.df_descartados[colset]
    apisafe.df_sospechosos = apisafe.df_sospechosos[colset]

    # Fill 'DESCARTADOS' until 23/3/2020 estimating with total and distribution of 24/3/2020
    df = apisafe.df_descartados.copy()
    cols = list(df.columns)
    last_day = '24/3/2020'
    for c in cols:
        if c == last_day:
            break
        df[c] = df[last_day] / df.loc['TOTAL'][last_day] * df.loc['TOTAL'][c]
    apisafe.df_descartados = df

    apisafe.df_confirmados['TYPE']='CONFIRMADOS'
    apisafe.df_descartados['TYPE']='DESCARTADOS'
    apisafe.df_sospechosos['TYPE']='SOSPECHOSOS'

    # We change department prefix from 'D_' to '#D_'. Also total row name is '##TOTAL' now:
    to_department = {_format_department(p): _format_department(d) for p,d in apisafe.to_department.items()}
    apisafe.df_confirmados.rename(index = {'TOTAL': '##TOTAL'}, inplace=True)
    apisafe.df_descartados.rename(index = {'TOTAL': '##TOTAL'}, inplace=True)
    apisafe.df_sospechosos.rename(index = {'TOTAL': '##TOTAL'}, inplace=True)
    to_department['##TOTAL']='##TOTAL'

    # Check index of 3 tables are the same (no missing entry).
    assert all(apisafe.df_confirmados.index==apisafe.df_descartados.index)
    assert all(apisafe.df_confirmados.index==apisafe.df_sospechosos.index)

    # Join 3 tables
    df_all = pd.concat([apisafe.df_confirmados,apisafe.df_descartados,apisafe.df_sospechosos])
    # Fill department column
    df_all.index = df_all.index.map(_format_department)
    df_all['DEPARTMENT'] = df_all.index
    df_all['DEPARTMENT'] = df_all['DEPARTMENT'].apply(lambda x : to_department[x])
    # MultiIndex by ['TYPE','DEPARTMENT','PLACE'] and sort the entries
    df_all = df_all.set_index('TYPE',append=True)
    df_all = df_all.set_index('DEPARTMENT',append=True)
    df_all = df_all.reorder_levels(['TYPE','DEPARTMENT','PLACE'])
    df_all = df_all.sort_index()

    df_all.to_csv('result_migration.csv')
