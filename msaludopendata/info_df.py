import pandas as pd
import world_bank_data as wb

from common import *
import info_gdf

def info_countries_df():
    countries = wb.get_countries()
    countries

    # Population dataset, by the World Bank (most recent value)
    population = wb.get_series('SP.POP.TOTL', mrv=1)
    population

    # Same data set, indexed with the country code
    population = wb.get_series('SP.POP.TOTL', id_or_value='id', simplify_index=True, mrv=1)
    population

    # Aggregate region, country and population
    df = countries[['region', 'latitude', 'longitude','name']].loc[countries.region != 'Aggregates']
    df['population'] = population
    df = df.reset_index().rename(columns={'id':'LOCATION'})
    df['LOCATION']=df['LOCATION'].apply(normalize_str)
    df['POPULATION']=df['population']

    gdf_indexed = info_gdf.GLOBAL_INFO_GDF.set_index('LOCATION')
    df = df.set_index('LOCATION')
    df['LAT'] = gdf_indexed['geometry'].centroid.apply(lambda p : p.coords[0][1])
    df['LONG'] = gdf_indexed['geometry'].centroid.apply(lambda p : p.coords[0][0])
    df = df.reset_index()

    df = df[['LOCATION','POPULATION', 'LAT', 'LONG','name']]

    df['name']=df['name'].apply(normalize_str)
    oldNames = [ "Brunei Darussalam", "Congo, Dem. Rep.", "Congo, Rep.", "Czech Republic", "Egypt, Arab Rep.",
                 "Iran, Islamic Rep.", "Korea, Rep.", "St. Lucia", "West Bank and Gaza", "Russian Federation",
                 "Slovak Republic", "United States", "St. Vincent and the Grenadines", "Venezuela, RB",
                 ]
    newNames = [ "Brunei", "Congo (Kinshasa)", "Congo (Brazzaville)", "Czechia", "Egypt", "Iran", "Korea, South",
                 "Saint Lucia", "occupied Palestinian territory", "Russia", "Slovakia", "US",
                 "Saint Vincent and the Grenadines", "Venezuela" ]
    name_replace = dict(zip(map(normalize_str,oldNames),map(normalize_str,newNames)))
    df['name']=df['name'].replace(name_replace)
    return df

def location_to_iso(df_info):
    location_to_iso = {r['name']:r['LOCATION'] for _,r in df_info.iterrows()}
    return location_to_iso

GLOBAL_INFO_DF = None
GLOBAL_LOCATION_TO_ISO_COUNTRIES = None

def info_df():
    global GLOBAL_INFO_DF, GLOBAL_LOCATION_TO_ISO_COUNTRIES

    df_info_world = info_countries_df()
    GLOBAL_LOCATION_TO_ISO_COUNTRIES = location_to_iso(df_info_world)

    df_info_arg = pd.read_csv(DATA_IN_CSV_INFO_ARG)
    GLOBAL_INFO_DF = pd.concat([df_info_world,df_info_arg],ignore_index=True)

info_df()
