import requests
import pandas as pd
import unicodedata
import datetime
import os

CSV_FOLDER = './csvs'

def touch_timestamp():
    # Save time of last update
    timestamp = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    with open(os.path.join(CSV_FOLDER,'last_update.txt'), 'w') as f:
        f.write('Last update on: {}'.format(timestamp))

def normalize_str(s):
    """ Function for name normalization (handle áéíóú). """
    return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii").upper()

def download_csv(url, csv_output_file):
    response = requests.get(url)
    assert response.status_code == 200,\
        'Wrong status code at dowloading from drive {}'.format(csv_output_file)
    f = open(csv_output_file, "wb")
    f.write(response.content)
    f.close()

def download_google_tables(drive_key, drive_uid_sheets):
    """ Download sheets from drive_key file. drive_uid_sheets must be
        [(drive_uid, output_filename)] """
    print('Download from google drive...')
    URL_TEMPLATE = 'https://docs.google.com/spreadsheet/ccc?key={}&output=csv&gid={}'

    for csv_filename, uid in drive_uid_sheets:
        download_csv(URL_TEMPLATE.format(drive_key, uid), csv_filename)
