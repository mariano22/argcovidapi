import numpy as np
import pandas as pd
import math
import collections
import os
from common import *

def _download_google_tables():
    """ Download sheets that feed the api from public drive:
    https://docs.google.com/spreadsheets/d/1RKS1coG0wkbqOmBi9xuguNeAdZKQZbQ6KGyc2yrQ8FY/edit#gid=0 """
    drive_key = '19aa5sqdsj3nYmBqllPXvgj72cvx63SzB2Hx8B02vMwU'
    drive_uid_sheets = [ ('fromdrive_SantaFe_AllData.csv', '1702343851') ]
    download_google_tables(drive_key, drive_uid_sheets)

COVIDStats = collections.namedtuple('COVIDStats', ['date', 'place_name', 'confirmados','descartados','sospechosos'])

def is_deparment(place_name):
    """ Function to check if a PLACE entry is a deparment. """
    return 'D_' in place_name

def is_city(place_name):
    """ Function to check if a PLACE entry is a city. """
    return not is_deparment(place_name) and 'TOTAL' not in place_name

def complete_deparments_and_total(df):
    """ Take a DataFrame with (TYPE, DEPARTMENT, PLACE) index and calculate
        '##TOTAL' and departments columns. """
    TYPE_INDEX, DEPARTMENT_INDEX, PLACE_INDEX = 0, 1, 2
    df = df.copy()
    # Only cities on df
    df_cities = df[df.index.map(lambda x : is_city(x[2]))].copy()
    # Group by department and shape similar to df
    df_departments = df_cities.groupby(['TYPE','DEPARTMENT']).sum().reset_index()
    df_departments['PLACE']=df_departments['DEPARTMENT']
    df_departments = df_departments.set_index(['TYPE','DEPARTMENT','PLACE'])
    # Group all cities and shape similar to df
    df_totals = df_cities.groupby(['TYPE']).sum().reset_index()
    df_totals['PLACE']='##TOTAL'
    df_totals['DEPARTMENT']='##TOTAL'
    df_totals = df_totals.set_index(['TYPE','DEPARTMENT','PLACE'])
    # Filter 'TOTAL' and departments rows and add the one that calculated
    df = df[ df.index.map(lambda i : '#' not in i[PLACE_INDEX]) ]
    df = pd.concat([df,df_departments,df_totals]).sort_index()
    return df

def _colide_names(df, name_predicate, new_name):
    is_named = df['PLACE'].apply(name_predicate)
    df_match = df[is_named].copy()
    df_match['PLACE']=normalize_str(new_name)
    df_match = df_match.groupby(['TYPE','DEPARTMENT','PLACE']).sum()

    df = pd.concat([ df[~is_named].copy().set_index(['TYPE','DEPARTMENT','PLACE']), df_match])
    df = df.reset_index()
    return df

def name_sanity(df):
    df = df.reset_index()
    df['PLACE'] = df['PLACE'].replace({
        'PUEBLO ANDINO':'ANDINO',
        'BERAVEBU':'BERABEVU',
        'SANTA ROSA DE CALCHINES':'SANTA ROSA',
        'SAN JERONIMO SUD':'SAN JERONIMO SUR',
        'PUEBLO IRIGOYEN':'IRIGOYEN',
        'DIAZ':'ESTACION DIAZ',
        'VILLA GOB. GALVEZ': 'VILLA GOBERNADOR GALVEZ',
        'CLASSON':'CLASON',
        'CAFFERATA':'CAFERATA',
    })

    df=_colide_names(df,lambda p : 'DOMINGUEZ' in p or 'CORONEL RODOLFO' in p ,'Coronel Dominguez')
    df=_colide_names(df,lambda p : 'PUERTO' in p and 'SAN MARTIN' in p ,'Puerto San Martin')
    df=_colide_names(df,lambda p : 'VILLA' in p and 'GALVEZ' in p ,'VILLA GOBERNADOR GALVEZ')
    df=df.set_index(['TYPE','DEPARTMENT','PLACE']).sort_index()
    return df

class SantaFeAPI:
    """" API for programatically get info about COVID situation at Santa Fe. """
    def __init__(self,work_dir, mock_drive=None):
        self.work_dir = work_dir

        # Download files from Google Drive COVIDSantaFe Dashboard
        if not mock_drive:
            _download_google_tables()

        # Load CSV's
        if mock_drive:
            self.df = read_place_table(mock_drive)
        else:
            self.df = read_place_table(os.path.join(self.work_dir, 'fromdrive_SantaFe_AllData.csv'))
        self.df = self.df.set_index('TYPE',append=True)
        self.df = self.df.set_index('DEPARTMENT',append=True)
        self.df = self.df.reorder_levels(['TYPE','DEPARTMENT','PLACE'])
        TYPE_INDEX, DEPARTMENT_INDEX, PLACE_INDEX = 0, 1, 2
        self.df = self.df.sort_index()

        # Rename some columns, colide synonyms cities
        self.df = name_sanity(self.df)

        # Get cities name
        self.all_names = set(index[PLACE_INDEX] for index in self.df.index)
        self.cities = set(n for n in self.all_names if is_city(n))
        self.departments = set(n for n in self.all_names if is_deparment(n))

        # Dict[place_name, department] assosciation
        self.to_department = { index[PLACE_INDEX]: index[DEPARTMENT_INDEX]
                                    for index in self.df.index }
        # Complete deparment rows by summing the cities.
        self.df = complete_deparments_and_total(self.df)

    def get_stats(self,date):
        """ Return a [ COVIDStats ] for the considered date. """
        result = []
        for place_name in self.all_names:
            result.append(COVIDStats(date        = date,
                                     place_name  = place_name,
                                     confirmados = self.df.loc['CONFIRMADOS'].loc[self.to_department[place_name]].loc[place_name][date],
                                     descartados = self.df.loc['DESCARTADOS'].loc[self.to_department[place_name]].loc[place_name][date],
                                     sospechosos = self.df.loc['SOSPECHOSOS'].loc[self.to_department[place_name]].loc[place_name][date]))
        return result
    def get_cities_stats(self,date):
        """ Return a [ COVIDStats ] for the cities only. """
        return [ s  for s in self.get_stats(date) if is_city(s.place_name) ]
    def get_departments_stats(self,date):
        """ Return a [ COVIDStats ] for the deparments only. """
        return [ s  for s in self.get_stats(date) if is_deparment(s.place_name) ]

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from IPython.display import IFrame
    import gmplot
    api = SantaFeAPI('./')
    date = '26/3/2020'
    ciudades = api.df_confirmados[ api.df_confirmados.index.map(is_city)  ][date]
    ciudades = ciudades[ciudades>0]
    if not ciudades.empty:
        ciudades.plot.bar()
        plt.savefig('confirmados.png', bbox_inches = 'tight')
    else:
        print('No confirmed cases at {}'.format(date))
