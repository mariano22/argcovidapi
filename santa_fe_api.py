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
    drive_uid_sheets = [ ('fromdrive_SantaFe_Confirmados.csv', '1708488423'),
                         ('fromdrive_SantaFe_Sospechosos.csv','973861334'),
                         ('fromdrive_SantaFe_Descartados.csv','1850124287'),
                         ('fromdrive_SantaFe_Info.csv','743139306') ]
    download_google_tables(drive_key, drive_uid_sheets)

CityInfo = collections.namedtuple('CityInfo', ['latitud','longitud','departamento'])
COVIDStats = collections.namedtuple('COVIDStats', ['date', 'place_name', 'confirmados','descartados','sospechosos'])

def is_city(place_name):
    """ Function to check if a PLACE entry is a city. """
    return place_name[:2]!='D_' and place_name!='TOTAL'

def is_deparment(place_name):
    """ Function to check if a PLACE entry is a deparment. """
    return place_name[:2]=='D_'

def complete_deparments(df,to_department):
    """ Complete department rows. to_department must map city names to department. """
    df = df.copy()
    df['DEPARTMENT'] = df.index
    df['DEPARTMENT'] = df['DEPARTMENT'].apply(lambda x : to_department[x])
    grouped_df = df.groupby(['DEPARTMENT']).sum()
    for place_name, _ in df.iterrows():
        if is_deparment(place_name):
            df.loc[place_name] = grouped_df.loc[place_name]
    return df.drop(columns=['DEPARTMENT'])

class SantaFeAPI:
    """" API for programatically get info about COVID situation at Santa Fe. """
    def __init__(self,work_dir, strict_sanity = False):
        self.work_dir = work_dir

        # Download files from Google Drive COVIDSantaFe Dashboard
        _download_google_tables()

        # Load CSV's
        self.df_info = read_place_table(os.path.join(self.work_dir, "fromdrive_SantaFe_Info.csv"))
        self.df_confirmados = read_place_table(os.path.join(self.work_dir, 'fromdrive_SantaFe_Confirmados.csv'))
        self.df_descartados = read_place_table(os.path.join(self.work_dir, 'fromdrive_SantaFe_Descartados.csv'))
        self.df_sospechosos = read_place_table(os.path.join(self.work_dir, 'fromdrive_SantaFe_Sospechosos.csv'))

        # Get cities name
        self.all_names = set( list(self.df_confirmados.index) +\
                              list(self.df_descartados.index) +\
                              list(self.df_sospechosos.index) )
        self.cities = set(n for n in self.all_names if is_city(n))
        self.departments = set(n for n in self.all_names if is_deparment(n))

        # Get the deperment of each city from 'Confirmados' table
        to_department = dict()
        curr_department = ''
        for place_name, _ in self.df_confirmados.iterrows():
            if is_deparment(place_name):
                curr_department = place_name
            to_department[place_name] = curr_department
        # Complete deparment rows by summing the cities.
        self.df_confirmados = complete_deparments(self.df_confirmados,to_department)
        self.df_descartados = complete_deparments(self.df_descartados,to_department)
        self.df_sospechosos = complete_deparments(self.df_sospechosos,to_department)

        # Check all places have 'Info' entry.
        sanity_ok = True
        for df in [self.df_confirmados, self.df_descartados, self.df_sospechosos]:
            for city_name, _ in df.iterrows():
                if city_name=='TOTAL':
                    continue
                if city_name not in self.df_info.index:
                    sanity_ok = False
                    print('Not info entry for: {}'.format(city_name))
        if strict_sanity:
            assert sanity_ok

        # Build city information dict
        self.city_information = { city_name:
            CityInfo(latitud = self.df_info['LATITUD'].get(city_name,0),
                     longitud = self.df_info['LONGITUD'].get(city_name,0),
                     departamento = to_department[city_name])
                        for city_name in self.cities }

    def get_stats(self,date):
        """ Return a [ COVIDStats ] for the considered date. """
        result = []
        for city_name in self.all_names:
            result.append(COVIDStats(date        = date,
                                     place_name  = city_name,
                                     confirmados = self.df_confirmados[date].get(city_name,0),
                                     descartados = self.df_descartados[date].get(city_name,0),
                                     sospechosos = self.df_sospechosos[date].get(city_name,0)))
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
