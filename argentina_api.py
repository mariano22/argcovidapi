import numpy as np
import pandas as pd
import math
import unicodedata
import collections
import os
from common import *

def _download_google_tables():
    """ Download sheets that feed the api from public drive:
    https://docs.google.com/spreadsheets/d/1xDi1RIXFA_cWaKJ-WEBRuFSrHwlFr7308NtQhoBLEsA/edit#gid=0 """
    drive_key = '1xDi1RIXFA_cWaKJ-WEBRuFSrHwlFr7308NtQhoBLEsA'
    drive_uid_sheets = [ ('fromdrive_Argentina_Test_Diff.csv', '787490104'),
                         ('fromdrive_Argentina_Confirmados_Diff.csv','1219039431'),
                         ('fromdrive_Argentina_Fallecidos_Diff.csv','219440205') ]
    download_google_tables(drive_key, drive_uid_sheets)

COVIDStats = collections.namedtuple('COVIDStats', ['date', 'place_name', 'confirmados','fallecidos'])

class ArgentinaAPI:
    """" API for programatically get info about COVID situation at Argentina provinces. """
    def __init__(self,work_dir):
        self.work_dir = work_dir

        # Download files from Google Drive COVIDSantaFe Dashboard
        _download_google_tables()

        # Load CSV's and pass to cumulative values
        self.df_test = pd.read_csv(os.path.join(self.work_dir, 'fromdrive_Argentina_Test_Diff.csv')).fillna(0).set_index('FECHA')
        for c in self.df_test.columns:
            self.df_test[c] = self.df_test[c].cumsum()

        self.df_confirmados = read_place_table(os.path.join(self.work_dir, 'fromdrive_Argentina_Confirmados_Diff.csv'))
        for province,_ in self.df_confirmados.iterrows():
            self.df_confirmados.loc[province] = self.df_confirmados.loc[province].cumsum()

        self.df_fallecidos = read_place_table(os.path.join(self.work_dir, 'fromdrive_Argentina_Fallecidos_Diff.csv'))
        for province,_ in self.df_fallecidos.iterrows():
            self.df_fallecidos.loc[province] = self.df_fallecidos.loc[province].cumsum()

    def get_stats(self,date):
        """ Return a [ COVIDStats ] for the considered date for all provinces """
        result = []
        for province_name, r in self.df_confirmados.iterrows():
            result.append(COVIDStats(date        = date,
                                     place_name  = province_name,
                                     confirmados = self.df_confirmados[date].get(province_name,0),
                                     fallecidos = self.df_fallecidos[date].get(province_name,0)))
        return result

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from IPython.display import IFrame
    import gmplot
    api = ArgentinaAPI('./')
    date = '26/3/2020'
    provinces = api.df_confirmados[date]
    provinces = provinces[provinces>0]
    if not provinces.empty:
        provinces.plot.bar()
        plt.savefig('confirmados_nacion.png', bbox_inches = 'tight')
    else:
        print('No confirmed cases at {}'.format(date))
