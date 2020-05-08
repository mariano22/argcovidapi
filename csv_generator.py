from common import *
from santa_fe_api import *
from argentina_api import *
import santa_fe_datosabiertos_joiner
import os

if __name__ == '__main__':
    # Erase old csv's.
    for fn in [ 'Argentina_Provinces.csv' ]:
        if os.path.exists(fn):
            os.remove(fn)
    touch_timestamp()
    # Generate Argentina csv's
    argentina_api = ArgentinaAPI('./')
    argentina_api.df_provinces.to_csv(os.path.join(CSV_FOLDER,'Argentina_Provinces.csv'))
    # Download and join data from Santa Fe datos abiertos portal
    santa_fe_datosabiertos_joiner.update_santa_fe()
