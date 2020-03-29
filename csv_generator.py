
from santa_fe_api import *
import datetime

if __name__ == '__main__':
    api = SantaFeAPI('./', strict_sanity = False)
    timestamp = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    api.df_info.to_csv('Info_{}.csv'.format(timestamp))
    api.df_confirmados.to_csv('Confirmados_{}.csv'.format(timestamp))
    api.df_descartados.to_csv('Descartados_{}.csv'.format(timestamp))
    api.df_sospechosos.to_csv('Sospechosos_{}.csv'.format(timestamp))
