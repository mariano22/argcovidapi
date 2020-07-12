import wget
import os

from common import *

REMOTE_CSV_CONFIRMADOS_WORLD = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
REMOTE_CSV_MUERTOS_WORLD = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
REMOTE_CSV_RECOVERED_WORLD = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
REMOTE_CSV_CASOS_ARG = 'https://sisa.msal.gov.ar/datos/descargas/covid-19/files/Covid19Casos.csv'

def download_csvs():
    to_download_url_and_paths = [
        (REMOTE_CSV_CONFIRMADOS_WORLD,   DATA_IN_CSV_CONFIRMADOS_WORLD),
        (REMOTE_CSV_MUERTOS_WORLD,       DATA_IN_CSV_MUERTOS_WORLD),
        (REMOTE_CSV_RECOVERED_WORLD,     DATA_IN_CSV_RECOVERED_WORLD),
        (REMOTE_CSV_CASOS_ARG,           DATA_IN_CSV_CASOS_ARG),
    ]
    print('Erasing prior version of the files...')
    for _, file_path in to_download_url_and_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
    print('Downloading updated csv\'s...')
    for url, file_path in to_download_url_and_paths:
        print('Downloading {}'.format(file_path))
        wget.download(url, file_path)