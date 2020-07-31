import pandas as pd
import numpy as np
import datetime
import unicodedata
import math
from geopy import distance,point

""" INPUT FILES """
DATA_IN_GEOJSON_ARG = 'data_in/maps_general.geojson'
DATA_IN_GEOJSON_WORLD = 'data_in/countries.geojson'
DATA_IN_CSV_INFO_ARG = 'data_in/info_general.csv'
DATA_IN_CSV_CONFIRMADOS_WORLD ='data_in/time_series_covid19_confirmed_global.csv'
DATA_IN_CSV_MUERTOS_WORLD = 'data_in/time_series_covid19_deaths_global.csv'
DATA_IN_CSV_RECOVERED_WORLD = 'data_in/time_series_covid19_recovered_global.csv'
DATA_IN_CSV_CASOS_ARG = 'data_in/Covid19Casos.csv'
DATA_IN_CSV_CASOS_CABA = 'data_in/casos_covid19_caba.csv'

""" Use ISO 8601 date format """
DATE_FORMAT = '%Y-%m-%d'

def normalize_str(s):
    """ Function for name normalization (handle áéíóú) """
    if type(s)==float:
        assert math.isnan(s)
        return ''
    return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii").upper().lstrip().rstrip()

def is_column_str(ts):
    """ Check if columns in ts are in str format (we work with str and pd.datetime formats). """
    return set(type(c) for c in ts.columns) == {str}

def fillna_time_series(df):
    """ Given a cumulative time serie, complete missing days.
        [ NaN NaN 1 2 Nan 3 NaN 4 4 NaN ] transform to [ 0 0 1 2 2 3 3 4 4 4 ] """
    for index, row in df.iterrows():
        new_row_data = [0]
        for _, value in row.iteritems():
            if math.isnan(value):
                new_row_data.append(new_row_data[-1])
            else:
                new_row_data.append(value)
        df.loc[index]=pd.Series(new_row_data[1:],index=row.index)
    return df

def check_days_consecutive(ts):
    """ Check i-column is the prior day of (i+1)-column.
        Support str and datetime column type. """
    if is_column_str(ts):
        ts = ts.rename(columns = lambda d : pd.to_datetime(d,format=DATE_FORMAT))
    cols = list(ts.columns)
    for i in range(1,len(cols)):
        assert cols[i]-cols[i-1]==datetime.timedelta(days=1)

def add_missing_columns(ts):
    """
    Dada una serie temporal acumulativa con posiblemente huecos de dias, hace que
    tenga todos los dias del dia minimo al dia maximo.
    """
    time_range = pd.date_range(ts.columns.min(), ts.columns.max())
    # Add missing columns
    new_columns = set(time_range).difference(set(ts.columns))
    for c in new_columns:
        ts[c]=math.nan
    # Sort columns
    ts=ts[sorted(ts.columns)]
    return ts

def correct_ts(ts):
    """ Main function to correct and check cumulative time series:
        cumulative ts -> Add missing dates -> Properly fill nan -> Check days are consecutive
        Support str and datetime column type.
    """
    # If columns are in str format transform to datetime (and go back to str at function end)
    transform_back_to_str = False
    if is_column_str(ts):
        ts = ts.rename(columns = lambda d : pd.to_datetime(d,format=DATE_FORMAT))
        transform_back_to_str = True

    ts = add_missing_columns(ts)
    ts = fillna_time_series(ts)
    check_days_consecutive(ts)

    if transform_back_to_str:
        ts=ts.rename(columns = lambda d : d.strftime(DATE_FORMAT))
    return ts

def concat_time_series(tss):
    """
    Concatena de manera segura una lista de series temporales acumulativas
    (pueden tener distintos rangos)
    """
    for i in range(len(tss)):
        check_days_consecutive(tss[i])
        tss[i]=tss[i].rename(columns = lambda d : pd.to_datetime(d,format=DATE_FORMAT))
    ts_result = pd.concat(tss)
    ts_result = correct_ts(ts_result)
    ts_result=ts_result.rename(columns = lambda d : d.strftime(DATE_FORMAT))
    return ts_result

def check_locations(locations_df,location_info_set,level=None,strict=False):
    """
        Chequea que los elementos de locations_df esten en location_info_set.
        Si level esta seteado solo analiza las location con cierto numero de '/'
        Si strict es True, ante un error crashea la ejecucion.
    """
    for location in locations_df:
        if location not in location_info_set and (level is None or location.count('/')==level):
            print("Location without info:\"{}\"".format(location))
            assert not strict

def add_per_capita(df, df_geoinfo, type_cols):
    """
    Dada una serie temporal (acumulada) con indice TYPE y LOCATION, calcula
    'colname'_PER100K para cada colname en type_cols.
    """
    # Add per capita fields
    df_per_capita = pd.merge((df*100000).reset_index(),df_geoinfo[['LOCATION','POPULATION']],on='LOCATION',how='left')
    df_per_capita = df_per_capita.fillna(math.inf).set_index(['TYPE','LOCATION'])
    df_per_capita = df_per_capita.div(df_per_capita['POPULATION'], axis=0)
    df_per_capita = df_per_capita.drop(columns=['POPULATION'])
    df_per_capita = df_per_capita[ df_per_capita.index.map(lambda x : x[0] in type_cols) ]
    df_per_capita.index = df_per_capita.index.map(lambda x : (x[0]+'_PER100K',x[1]) )
    df = pd.concat([df,df_per_capita]).sort_index()
    return df.sort_index()

def add_duplication_time(df):
    """
    Dada una serie temporal (acumulada) con indice TYPE y LOCATION, calcula
    DUPLICATION_TIME de CONFIRMADOS
    """
    ts = df.loc['CONFIRMADOS'].copy()
    date_format = '%Y-%m-%d'
    ts=ts.rename(columns = lambda d : pd.to_datetime(d,format=date_format))
    for location in set(ts.index):
        row = ts.loc[location]
        row_list = list(row.iteritems())
        j = 0
        new_row_list = []
        for i in range(len(row_list)):
            while j<i and j+1<len(row_list) and row_list[j+1][1]*2 <= row_list[i][1]:
                j+=1
            new_row_list.append((row_list[i][0]-row_list[j][0]).days)
        new_row = pd.Series(new_row_list, index=row.index)
        ts.loc[location] = new_row
    ts=ts.reset_index()
    ts['TYPE']='DUPLICATION_TIME'
    ts=ts.set_index(['TYPE','LOCATION']).sort_index()
    ts=ts.rename(columns = lambda d : d.strftime(date_format))
    return pd.concat([df,ts]).sort_index()

def add_cfr(df):
    """
    Dada una serie temporal (acumulada) con indice TYPE y LOCATION, calcula
    Case Fatality Rate (MUERTOS / CONFIRMADOS)
    """
    df_cfr = (df.loc['MUERTOS']/df.loc['CONFIRMADOS']).fillna(0)
    df_cfr['TYPE']='CFR'
    df_cfr=df_cfr.reset_index().set_index(['TYPE','LOCATION'])
    df=pd.concat([df,df_cfr])
    return df

def add_uci_ratio(df):
    """
    Dada una serie temporal (acumulada) con indice TYPE y LOCATION, calcula
    UCI_RATIO (UCI / CONFIRMADOS)
    """
    df_cfr = (df.loc['UCI']/df.loc['CONFIRMADOS']).fillna(0)
    df_cfr['TYPE']='UCI_RATIO'
    df_cfr=df_cfr.reset_index().set_index(['TYPE','LOCATION'])
    df=pd.concat([df,df_cfr])
    return df

def add_confirmados_diff(ts, periods=7):
    """ Calcula los nuevos confirmados en una serie temporal en periodos de
        longitud periods. El nuevo campo se llamara CONFIRMADOS_DIFF """
    confirmados = ts.loc['CONFIRMADOS']
    confirmados_diff = confirmados-confirmados.shift(periods=periods,axis=1).fillna(0)
    confirmados_diff = confirmados_diff.reset_index()
    confirmados_diff['TYPE'] = 'CONFIRMADOS_DIFF'
    confirmados_diff = confirmados_diff.set_index(['TYPE','LOCATION'])
    ts = pd.concat([ts,confirmados_diff]).sort_index()
    return ts

def add_min_dist(df):
    """ Dada una tabla con columnas ('LOCATION', 'LAT', 'LONG') agrega columna
        'MIN_DIST' con la minima distancia de cada LOCATION a otra. """
    print('Adding MIN_DIST...')
    df=df.set_index('LOCATION')
    df=df[~df['LAT'].isna() & ~df['LONG'].isna()]
    min_dist_data = []
    for location_1,r_1 in df.iterrows():
        min_dist_location = ''
        min_dist = 10000000
        for location_2,r_2 in df.iterrows():
            p_1=point.Point(latitude=r_1['LAT'], longitude=r_1['LONG'])
            p_2=point.Point(latitude=r_2['LAT'], longitude=r_2['LONG'])
            dist = distance.distance(p_1, p_2).km
            if location_1!=location_2 and min_dist>dist:
                min_dist = dist
                min_dist_location = location_2
        assert min_dist_location!=''
        min_dist_data.append(min_dist)
    df['MIN_DIST'] = pd.Series(index=df.index,data=min_dist_data)
    return df.reset_index()
