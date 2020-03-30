
from santa_fe_api import *
from argentina_api import *
import datetime
import os

if __name__ == '__main__':
    # Erase old csv's.
    for fn in [ 'SantaFe_Confirmados.csv', 'SantaFe_Descartados.csv',
                'SantaFe_Sospechosos.csv', 'SantaFe_Info.csv',
                'Argentina_Tests.csv', 'Argentina_Confirmados.csv',
                'Argentina_Fallecidos.csv' ]:
        if os.path.exists(fn):
            os.remove(fn)
    # Save time of last update
    timestamp = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    with open('last_update.txt', 'w') as f:
        f.write('Last update on: {}'.format(timestamp))
    # Generate Santa Fe csv's
    santa_fe_api = SantaFeAPI('./', strict_sanity = False)
    santa_fe_api.df_info.to_csv('SantaFe_Info.csv')
    santa_fe_api.df_confirmados.to_csv('SantaFe_Confirmados.csv')
    santa_fe_api.df_descartados.to_csv('SantaFe_Descartados.csv')
    santa_fe_api.df_sospechosos.to_csv('SantaFe_Sospechosos.csv')
    # Generate Argentina csv's
    argentina_api = ArgentinaAPI('./')
    argentina_api.df_test.to_csv('Argentina_Tests.csv')
    argentina_api.df_confirmados.to_csv('Argentina_Confirmados.csv')
    argentina_api.df_fallecidos.to_csv('Argentina_Fallecidos.csv')
