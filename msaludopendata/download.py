import wget
import os

from common import *

REMOTE_CSV_CONFIRMADOS_WORLD = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
REMOTE_CSV_MUERTOS_WORLD = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
REMOTE_CSV_RECOVERED_WORLD = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
REMOTE_CSV_CASOS_ARG = 'https://sisa.msal.gov.ar/datos/descargas/covid-19/files/Covid19Casos.csv'
REMOTE_CSV_CASOS_CABA = 'https://cdn.buenosaires.gob.ar/datosabiertos/datasets/salud/casos-covid-19/casos_covid19.csv'

def download_csvs():
    to_download_url_and_paths = [
        (REMOTE_CSV_CONFIRMADOS_WORLD,   DATA_IN_CSV_CONFIRMADOS_WORLD),
        (REMOTE_CSV_MUERTOS_WORLD,       DATA_IN_CSV_MUERTOS_WORLD),
        (REMOTE_CSV_RECOVERED_WORLD,     DATA_IN_CSV_RECOVERED_WORLD),
        (REMOTE_CSV_CASOS_ARG,           DATA_IN_CSV_CASOS_ARG),
        (REMOTE_CSV_CASOS_CABA,          DATA_IN_CSV_CASOS_CABA),
    ]
    print('Downloading updated csv\'s...')
    for url, file_path in to_download_url_and_paths:
        tmp_path = file_path+'.bak'
        print('Downloading {}...'.format(file_path))
        try:
            wget.download(url, tmp_path)
            if os.path.exists(tmp_path):
                if os.path.exists(file_path):
                    os.remove(file_path)
                os.rename(tmp_path,file_path)
                os.remove(tmp_path)
        except:
            print('Error downloading {}, checking all version exists...'.format(file_path))
            assert os.path.exists(file_path)
