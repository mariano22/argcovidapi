from tabula import read_pdf
from itertools import *
import os
import sys
import pandas as pd
import numpy as np
from contextlib import contextmanager

import sys
sys.path.append('..')
from common import *

_COLUMNAS = ['Departamento/ Localidad','Confirmados','Descartados','Sospechosos','Total']

def _fill_department(place_name):
    """ Given the place name deduce if it's a department by seeing lowercase/uppercase and add '#D_' prefix """
    is_dep = any([x.islower() for x in place_name])
    place_name = normalize_str(place_name)
    if place_name=='TOTAL':
        return '##TOTAL'
    return ('#D_' if is_dep else '') + place_name

def _normal_proc(df):
    """ General processing for all the pages """
    df = df.fillna(0)
    df = df.rename(columns = {'Confirmado': 'Confirmados',
                             'Descartado': 'Descartados',
                             'Sospechoso': 'Sospechosos'
                            })
    if df['Total'].sum()==0 and 'Unnamed: 0' in df.columns:
        df['Total'] = df['Unnamed: 0']
        df = df.drop(columns='Unnamed: 0')
    assert set(df.columns) == set(_COLUMNAS)
    df['Departamento/ Localidad']=df['Departamento/ Localidad'].apply(_fill_department)
    return df

def _default_colval(col):
   """ In non first parsed tables headers are data rows and must be interpreted. """
   return ( 0 if col.startswith('Unnamed') else int(float(col)) )

def _second_pages(df):
    """ Processing for succesive pages (header are deduced). """
    df = df.fillna(0)
    to_delete = [col for col in df.columns if col.startswith('Unnamed') and len(df[df[col]==0])>=(len(df)*0.95)]
    for c in to_delete:
        for _,place_warn in df[df[c]>0][df.columns[0]].iteritems():
            print('Warning at place: {}'.format(place_warn))
    df = df.drop(columns=to_delete)
    assert len(df.columns)==5
    df_head = pd.DataFrame(data = [ [df.columns[0]] + [ _default_colval(c) for c in df.columns[1:] ] ], columns=_COLUMNAS)
    df = df.rename(columns = { df.columns[i]: _COLUMNAS[i] for i in range(5) })
    df = pd.concat([df_head,df])
    return df

@contextmanager
def _suppress_stdout_stderr():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

def parse_pdf(in_pdf_filepath, out_csv_filepath):
    """ Read, parse and process PDF report and produce a CSV """
    print('Parsing pdf...')
    with _suppress_stdout_stderr():
        dfs = read_pdf(in_pdf_filepath, multiple_tables=True, pages='all')
    df_list = [_normal_proc(dfs[0])]
    print('Processing sheet 1 of table PDF...')
    for i in range(1,len(dfs)-1):
        print('Processing sheet {} of table PDF...'.format(i+1))
        df = _second_pages(dfs[i])
        df = _normal_proc(df)
        df_list.append(df)
    df_result = pd.concat(df_list, ignore_index=True)
    df_result.to_csv(out_csv_filepath, index = False)
    print('Finished!')

if __name__ == '__main__':
    usage = ''' Usage:
    python pdf_santa_fe_parser.py reporte.pdf output.csv '''
    if len(sys.argv)!=3:
        print(usage)
        exit(0)
    parse_pdf(sys.argv[1], sys.argv[2])
