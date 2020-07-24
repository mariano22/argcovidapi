"""
Calcula tabla con LOCATION, POPULATION, LAT, LONG y guarda en variable global GLOBAL_INFO_DF
Calcula diccionario NAME_COUNTRY -> ISO_COUNTRY y guarda en variable global GLOBAL_LOCATION_TO_ISO_COUNTRIES
"""
import pandas as pd
import world_bank_data as wb

from common import *
import info_gdf

def info_countries_df():
    countries = wb.get_countries()

    # Population dataset, by the World Bank (most recent value), indexed with the country code
    population = wb.get_series('SP.POP.TOTL', id_or_value='id', simplify_index=True, mrv=1)
    # PATCH: if last line is not working (sometimes World Bank doesn't work) replace with the line below
    # population = pd.read_csv('countries_population.csv').set_index('id')['population']

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
    name_replace = {
        'Brunei Darussalam': 'Brunei',
        'Congo, Dem. Rep.': 'Congo (Kinshasa)',
        'Congo, Rep.': 'Congo (Brazzaville)',
        'Czech Republic': 'Czechia',
        'Egypt, Arab Rep.': 'Egypt',
        'Iran, Islamic Rep.': 'Iran',
        'Korea, Rep.': 'Korea, South',
        'St. Lucia': 'Saint Lucia',
        'Russian Federation': 'Russia',
        'Slovak Republic': 'Slovakia',
        'United States': 'US',
        'St. Vincent and the Grenadines': 'Saint Vincent and the Grenadines',
        'Venezuela, RB': 'Venezuela',
        'Taiwan, China': 'Taiwan*',
        'Lao PDR': 'Laos',
        'Syrian Arab Republic': 'Syria',
        'BAHAMAS, THE': 'Bahamas',
        'ST. KITTS AND NEVIS': 'SAINT KITTS AND NEVIS',
        'KYRGYZ REPUBLIC': 'KYRGYZSTAN',
        'GAMBIA, THE': 'GAMBIA',
        'MYANMAR': 'BURMA',
        'YEMEN, REP.': 'YEMEN',
    }
    name_replace = { normalize_str(k): normalize_str(v) for k,v in name_replace.items() }
    df['name']=df['name'].replace(name_replace)
    return df

def location_to_iso(df_info):
    location_to_iso = {r['name']:r['LOCATION'] for _,r in df_info.iterrows()}
    return location_to_iso

GLOBAL_INFO_DF = None
GLOBAL_LOCATION_TO_ISO_COUNTRIES = None
GLOBAL_BARRIOS_TO_COMUNA = None

def info_df():
    global GLOBAL_INFO_DF, GLOBAL_LOCATION_TO_ISO_COUNTRIES, GLOBAL_BARRIOS_TO_COMUNA

    df_info_world = info_countries_df()
    GLOBAL_LOCATION_TO_ISO_COUNTRIES = location_to_iso(df_info_world)

    df_info_arg = pd.read_csv(DATA_IN_CSV_INFO_ARG)
    GLOBAL_INFO_DF = pd.concat([df_info_world,df_info_arg],ignore_index=True)

    df_caba = GLOBAL_INFO_DF[GLOBAL_INFO_DF['LOCATION'].apply(
        lambda l: l.startswith('ARGENTINA/CABA/') and l.count('/')==3 )].copy()
    GLOBAL_BARRIOS_TO_COMUNA = [ r['LOCATION'].split('/') for _,r in df_caba.iterrows() ]
    GLOBAL_BARRIOS_TO_COMUNA = { barrio:comuna for _, _, comuna, barrio in GLOBAL_BARRIOS_TO_COMUNA }

info_df()
