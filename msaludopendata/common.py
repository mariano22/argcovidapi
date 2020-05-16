import pandas as pd
import numpy as np
import datetime
import unicodedata
import math

DATA_IN_GEOJSON_ARG = 'data_in/maps_general.geojson'
DATA_IN_GEOJSON_WORLD = 'data_in/countries.geojson'
DATA_IN_CSV_INFO_ARG = 'data_in/info_general.csv'
DATA_IN_CSV_CONFIRMADOS_US = 'data_in/confirmed_us.csv'
DATA_IN_CSV_CONFIRMADOS_WORLD ='data_in/confirmed_global.csv'
DATA_IN_CSV_MUERTOS_US = 'data_in/death_us.csv'
DATA_IN_CSV_MUERTOS_WORLD = 'data_in/death_global.csv'
DATA_IN_CSV_CASOS_ARG = 'data_in/covid19casos.csv'

DATE_FORMAT = '%Y-%m-%d'

def normalize_str(s):
    """ Function for name normalization (handle áéíóú) """
    return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii").upper()

def correct_time_series(df):
    """ Given a time serie: [ NaN NaN 1 2 Nan 3 NaN 4 4 NaN ] transform to [ 0 0 1 2 2 3 3 4 4 4 ]"""
    for index, row in df.iterrows():
        new_row_data = [0]
        for _, value in row.iteritems():
            if value>0:
                new_row_data.append(value)
            else:
                new_row_data.append(new_row_data[-1])
        df.loc[index]=pd.Series(new_row_data[1:],index=row.index)
    return df

def check_locations(locations_df,location_info_set,level=None,strict=False):
    for location in locations_df:
        if location not in location_info_set and (level is None or location.count('/')==level):
            print("Location without info:{}".format(location))
            assert not strict

def add_per_capita(df, df_geoinfo, type_cols):
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
    df_cfr = (df.loc['MUERTOS']/df.loc['CONFIRMADOS']).fillna(0)
    df_cfr['TYPE']='CFR'
    df_cfr=df_cfr.reset_index().set_index(['TYPE','LOCATION'])
    df=pd.concat([df,df_cfr])
    return df
