import requests
import pandas as pd
import numpy as np

from common import *

def _set_provincia_name(s):
    if type(s) != str: return s
    if 'PROVICIA' in normalize_str(s).split():
        return 'PROVINCIA'
    return s
def _is_date(s):
    if type(s) != str: return False
    return len(s)==5 and s[2]=='/' and all(s[i].isdigit() for i in range(5) if i!=2)
def _valid_provincia(s):
    if type(s) != str: return False
    return any( caso in s.split() for caso in ['Confirmados','Recuperados','Muertos','Activos'] ) and 'Total' not in s.split()
def _get_type(s):
    return normalize_str(s.split()[-1])
def _get_provincia(s):
    col_map = {'BS AS': 'BUENOS AIRES',
            'CA3RDOBA': 'CORDOBA',
            'ENTRE RAOS': 'ENTRE RIOS',
            'RAONEGRO': 'RIO NEGRO',
            'SANTIAGO EST': 'SANTIAGO DEL ESTERO',
            'TIERRA DEL F': 'TIERRA DEL FUEGO',
            'RAO NEGRO': 'RIO NEGRO',
            }
    s = normalize_str(' '.join(s.split()[:-2]))
    return col_map.get(s,s)

def download_province_table():
    """ Download table with 'CONFIRMADOS' 'ACTIVOS' 'RECUPERADOS' and 'MUERTOS' per province.
        Preprocess and parse the downloaded table. """
    # Download table
    url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTfinng5SDBH9RSJMHJk28dUlW3VVSuvqaBSGzU-fYRTVLCzOkw1MnY17L2tWsSOppHB96fr21Ykbyv/pub#'
    print('Downloading Argentinian provinces table from google drive ({})'.format(url))
    TEMPORAL_HTML_FILE = 'fromdrive_per_province.html'
    r = requests.get(url)
    assert r.status_code == 200, 'Wrong status code at dowloading provinces table'
    with open(TEMPORAL_HTML_FILE, 'w') as out_f:
        out_f.write(r.content.decode("utf-8") )
    # Preprocess it
    dfs = pd.read_html(TEMPORAL_HTML_FILE)
    # Get first page table
    df = dfs[0]
    # Get the headers from first row
    df = df.rename(columns={ col: real_col for col,real_col in df.loc[0].iteritems() })
    # Rename the province column
    df = df.rename(columns=_set_provincia_name)
    # Erase 'trash' columns
    relevant_cols = ['PROVINCIA'] + [ col for col in df.columns if _is_date(col) ]
    df = df[relevant_cols]
    # Erase 'trash' rows
    df = df[df['PROVINCIA'].apply(_valid_provincia)]
    df = df.fillna(0)
    # Set indexes by type (confirmados, muertos, recuperados, activos) and province
    df['TYPE'] = df['PROVINCIA'].apply(_get_type)
    df['PROVINCIA'] = df['PROVINCIA'].apply(_get_provincia)
    df = df.set_index(['TYPE','PROVINCIA']).sort_index()
    for c in df.columns:
        df[c] = pd.to_numeric(df[c])
    return df
