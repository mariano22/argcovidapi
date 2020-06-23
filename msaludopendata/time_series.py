import pandas as pd
import numpy as np
import os
import datetime

from common import *
import ts_countries
import ts_arg
import info_df
import info_gdf

def ts_check_locations(ts):
    print('Checking locations INFO')
    check_locations(set(ts.reset_index()['LOCATION']), set(info_df.GLOBAL_INFO_DF['LOCATION']))
    print('Checking locations GEODATA')
    check_locations(set(ts.reset_index()['LOCATION']), set(info_gdf.GLOBAL_INFO_GDF['LOCATION']))

def time_series():
    df_ts_countries = ts_countries.ts_countries(info_df.GLOBAL_LOCATION_TO_ISO_COUNTRIES)
    df_ts_arg = ts_arg.ts_arg()
    ts = concat_time_series([df_ts_arg,df_ts_countries])

    ts = add_per_capita(ts,info_df.GLOBAL_INFO_DF, ['CONFIRMADOS','MUERTOS'])
    ts = add_duplication_time(ts)
    ts = add_cfr(ts)
    ts = add_uci_ratio(ts)
    ts_check_locations(ts)
    return ts

def time_series_only_countries():
    ts = ts_countries.ts_countries(info_df.GLOBAL_LOCATION_TO_ISO_COUNTRIES)
    ts = add_per_capita(ts,info_df.GLOBAL_INFO_DF, ['CONFIRMADOS','MUERTOS'])
    ts = add_duplication_time(ts)
    ts = add_cfr(ts)
    ts_check_locations(ts)
    return ts

def time_series_only_arg():
    ts = ts_arg.ts_arg()
    ts = add_per_capita(ts,info_df.GLOBAL_INFO_DF, ['CONFIRMADOS','MUERTOS'])
    ts = add_duplication_time(ts)
    ts = add_cfr(ts)
    ts = add_uci_ratio(ts)
    ts_check_locations(ts)
    return ts
