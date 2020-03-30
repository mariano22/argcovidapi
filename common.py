import requests
import pandas as pd
import unicodedata

def read_place_table(csv_filepath):
    df = pd.read_csv(csv_filepath).fillna(0)
    df['PLACE'] = df['PLACE'].map(normalize_str)
    return df.set_index('PLACE')

def normalize_str(s):
    """ Function for name normalization (handle áéíóú). """
    return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii").upper()

def download_google_tables(drive_key, drive_uid_sheets):
    """ Download sheets from drive_key file. drive_uid_sheets must be
        [(drive_uid, output_filename)] """
    print('Download from google drive...')
    URL_TEMPLATE = 'https://docs.google.com/spreadsheet/ccc?key={}&output=csv&gid={}'

    for csv_filename, uid in drive_uid_sheets:
        response = requests.get(URL_TEMPLATE.format(drive_key, uid))
        assert response.status_code == 200,\
            'Wrong status code at dowloading from drive {}'.format(csv_filename)
        f = open(csv_filename, "wb")
        f.write(response.content)
        f.close()
