import numpy as np
import pandas as pd
import math
import unicodedata
import collections
import os
from common import *
from argentina_province_parse import *

COVIDStats = collections.namedtuple('COVIDStats', ['date', 'place_name', 'confirmados','muertos', 'recuperados', 'activos'])

class ArgentinaAPI:
    """" API for programatically get info about COVID situation at Argentina provinces. """
    def __init__(self,work_dir):
        self.work_dir = work_dir

        # Download files from Google Drive
        self.df_provinces = download_province_table()
        self.provinces = list(self.df_provinces.loc['CONFIRMADOS'].index)

    def get_stats(self,date):
        """ Return a [ COVIDStats ] for the considered date for all provinces """
        result = []
        for province_name in self.provinces:
            result.append(COVIDStats(date        = date,
                                     place_name  = province_name,
                                     confirmados = self.df_provinces.loc['CONFIRMADOS'].loc[province_name][date],
                                     muertos = self.df_provinces.loc['MUERTOS'].loc[province_name][date],
                                     recuperados = self.df_provinces.loc['RECUPERADOS'].loc[province_name][date],
                                     activos = self.df_provinces.loc['ACTIVOS'].loc[province_name][date]))
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
