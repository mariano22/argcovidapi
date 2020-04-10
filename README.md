# Argentina and Santa Fe COVID API

Based on handed scraped data on goverment reports:
- Argentina: https://docs.google.com/spreadsheets/d/e/2PACX-1vTfinng5SDBH9RSJMHJk28dUlW3VVSuvqaBSGzU-fYRTVLCzOkw1MnY17L2tWsSOppHB96fr21Ykbyv/pub#
- Santa Fe: https://docs.google.com/spreadsheets/d/19aa5sqdsj3nYmBqllPXvgj72cvx63SzB2Hx8B02vMwU

Santa Fe reports are cumulative. National reports shows new daily cases.

We decided to work with cumulatives time series. There is a smart design decision behind that: if we have cumulative confirmed cases, we don't have to read all the entries, only with the frequentcy we are interested in (imagine weekly analysis).

'Sospechosos' could decrease because some cases can move to 'Confirmados' o 'Descartados'.

# Non-Python users

For non python users csv's are generated periodically to be parsed and used (see <code>./csv/ folder</code>). All with cumulative time series.
- For Santa Fe:

<code>csv/SantaFe_Confirmados.csv</code> <code>csv/SantaFe_Sospechosos.csv</code> <code>SantaFe_Descartados.csv</code>

- For Argentina:

<code>csv/Argentina_Provinces.csv</code>

Check last update time on <code>csv/last_update.txt</code>


## Argentina API

Python API for working with Argentina COVID data reported.

DataTypes exported:
- COVIDStats namedtuple
- ArgentinaAPI class

API methods:
- api.get_stats(date)
API public properties:
- api.df_test : pandas.DataFrame
- api.df_confirmados : pandas.DataFrame
- api.df_fallecidos : pandas.DataFrame

### Important data types.


```python
from argentina_api import *
print('COVIDStats namedtuple:', COVIDStats._fields)
```

    COVIDStats namedtuple: ('date', 'place_name', 'confirmados', 'muertos', 'recuperados', 'activos')


## Create api instance passing the working directory 
When load the data the API tells if there are no entries in 'Info' sheet for certain city.


```python
api = ArgentinaAPI('./')
```

### <code>get_stats : Date -> [ COVIDStats ]</code> of all provinces
Date must be expressd in DD/MM format.


```python
api.get_stats('26/03')[:3]
```




    [COVIDStats(date='26/03', place_name='BUENOS AIRES', confirmados=158, muertos=4, recuperados=15, activos=139),
     COVIDStats(date='26/03', place_name='CABA', confirmados=197, muertos=4, recuperados=53, activos=140),
     COVIDStats(date='26/03', place_name='CATAMARCA', confirmados=0, muertos=0, recuperados=0, activos=0)]



### Exported DataFrames
Also exports a DataFrame <code>df_provinces</code>.

With the content of Google Drive data by province (see link above). Provinces names are normalized using normalize_str function.


```python
api.df_provinces.head(3)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>03/03</th>
      <th>04/03</th>
      <th>05/03</th>
      <th>06/03</th>
      <th>07/03</th>
      <th>08/03</th>
      <th>09/03</th>
      <th>10/03</th>
      <th>11/03</th>
      <th>12/03</th>
      <th>...</th>
      <th>25/03</th>
      <th>26/03</th>
      <th>27/03</th>
      <th>28/03</th>
      <th>29/03</th>
      <th>30/03</th>
      <th>31/03</th>
      <th>01/04</th>
      <th>02/04</th>
      <th>03/04</th>
    </tr>
    <tr>
      <th>TYPE</th>
      <th>PROVINCIA</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="3" valign="top">ACTIVOS</th>
      <th>BUENOS AIRES</th>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>2</td>
      <td>2</td>
      <td>3</td>
      <td>3</td>
      <td>4</td>
      <td>5</td>
      <td>9</td>
      <td>...</td>
      <td>129</td>
      <td>139</td>
      <td>172</td>
      <td>181</td>
      <td>196</td>
      <td>230</td>
      <td>247</td>
      <td>255</td>
      <td>289</td>
      <td>308</td>
    </tr>
    <tr>
      <th>CABA</th>
      <td>1</td>
      <td>1</td>
      <td>1</td>
      <td>5</td>
      <td>5</td>
      <td>7</td>
      <td>8</td>
      <td>9</td>
      <td>10</td>
      <td>13</td>
      <td>...</td>
      <td>125</td>
      <td>140</td>
      <td>169</td>
      <td>184</td>
      <td>197</td>
      <td>231</td>
      <td>250</td>
      <td>259</td>
      <td>283</td>
      <td>311</td>
    </tr>
    <tr>
      <th>CATAMARCA</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>3 rows × 32 columns</p>
</div>



<code>df_provinces</code> have a MultiIndex of level 2


```python
api.df_provinces.index
```




    MultiIndex([(    'ACTIVOS',        'BUENOS AIRES'),
                (    'ACTIVOS',                'CABA'),
                (    'ACTIVOS',           'CATAMARCA'),
                (    'ACTIVOS',               'CHACO'),
                (    'ACTIVOS',              'CHUBUT'),
                (    'ACTIVOS',             'CORDOBA'),
                (    'ACTIVOS',          'CORRIENTES'),
                (    'ACTIVOS',          'ENTRE RIOS'),
                (    'ACTIVOS',             'FORMOSA'),
                (    'ACTIVOS',               'JUJUY'),
                (    'ACTIVOS',            'LA PAMPA'),
                (    'ACTIVOS',            'LA RIOJA'),
                (    'ACTIVOS',             'MENDOZA'),
                (    'ACTIVOS',            'MISIONES'),
                (    'ACTIVOS',             'NEUQUEN'),
                (    'ACTIVOS',           'RAO NEGRO'),
                (    'ACTIVOS',               'SALTA'),
                (    'ACTIVOS',            'SAN JUAN'),
                (    'ACTIVOS',            'SAN LUIS'),
                (    'ACTIVOS',          'SANTA CRUZ'),
                (    'ACTIVOS',            'SANTA FE'),
                (    'ACTIVOS', 'SANTIAGO DEL ESTERO'),
                (    'ACTIVOS',    'TIERRA DEL FUEGO'),
                (    'ACTIVOS',             'TUCUMAN'),
                ('CONFIRMADOS',        'BUENOS AIRES'),
                ('CONFIRMADOS',                'CABA'),
                ('CONFIRMADOS',           'CATAMARCA'),
                ('CONFIRMADOS',               'CHACO'),
                ('CONFIRMADOS',              'CHUBUT'),
                ('CONFIRMADOS',             'CORDOBA'),
                ('CONFIRMADOS',          'CORRIENTES'),
                ('CONFIRMADOS',          'ENTRE RIOS'),
                ('CONFIRMADOS',             'FORMOSA'),
                ('CONFIRMADOS',               'JUJUY'),
                ('CONFIRMADOS',            'LA PAMPA'),
                ('CONFIRMADOS',            'LA RIOJA'),
                ('CONFIRMADOS',             'MENDOZA'),
                ('CONFIRMADOS',            'MISIONES'),
                ('CONFIRMADOS',             'NEUQUEN'),
                ('CONFIRMADOS',           'RAO NEGRO'),
                ('CONFIRMADOS',               'SALTA'),
                ('CONFIRMADOS',            'SAN JUAN'),
                ('CONFIRMADOS',            'SAN LUIS'),
                ('CONFIRMADOS',          'SANTA CRUZ'),
                ('CONFIRMADOS',            'SANTA FE'),
                ('CONFIRMADOS', 'SANTIAGO DEL ESTERO'),
                ('CONFIRMADOS',    'TIERRA DEL FUEGO'),
                ('CONFIRMADOS',             'TUCUMAN'),
                (    'MUERTOS',        'BUENOS AIRES'),
                (    'MUERTOS',                'CABA'),
                (    'MUERTOS',           'CATAMARCA'),
                (    'MUERTOS',               'CHACO'),
                (    'MUERTOS',              'CHUBUT'),
                (    'MUERTOS',             'CORDOBA'),
                (    'MUERTOS',          'CORRIENTES'),
                (    'MUERTOS',          'ENTRE RIOS'),
                (    'MUERTOS',             'FORMOSA'),
                (    'MUERTOS',               'JUJUY'),
                (    'MUERTOS',            'LA PAMPA'),
                (    'MUERTOS',            'LA RIOJA'),
                (    'MUERTOS',             'MENDOZA'),
                (    'MUERTOS',            'MISIONES'),
                (    'MUERTOS',             'NEUQUEN'),
                (    'MUERTOS',           'RAO NEGRO'),
                (    'MUERTOS',               'SALTA'),
                (    'MUERTOS',            'SAN JUAN'),
                (    'MUERTOS',            'SAN LUIS'),
                (    'MUERTOS',          'SANTA CRUZ'),
                (    'MUERTOS',            'SANTA FE'),
                (    'MUERTOS', 'SANTIAGO DEL ESTERO'),
                (    'MUERTOS',    'TIERRA DEL FUEGO'),
                (    'MUERTOS',             'TUCUMAN'),
                ('RECUPERADOS',        'BUENOS AIRES'),
                ('RECUPERADOS',                'CABA'),
                ('RECUPERADOS',           'CATAMARCA'),
                ('RECUPERADOS',               'CHACO'),
                ('RECUPERADOS',              'CHUBUT'),
                ('RECUPERADOS',             'CORDOBA'),
                ('RECUPERADOS',          'CORRIENTES'),
                ('RECUPERADOS',          'ENTRE RIOS'),
                ('RECUPERADOS',             'FORMOSA'),
                ('RECUPERADOS',               'JUJUY'),
                ('RECUPERADOS',            'LA PAMPA'),
                ('RECUPERADOS',            'LA RIOJA'),
                ('RECUPERADOS',             'MENDOZA'),
                ('RECUPERADOS',            'MISIONES'),
                ('RECUPERADOS',             'NEUQUEN'),
                ('RECUPERADOS',           'RAO NEGRO'),
                ('RECUPERADOS',               'SALTA'),
                ('RECUPERADOS',            'SAN JUAN'),
                ('RECUPERADOS',            'SAN LUIS'),
                ('RECUPERADOS',          'SANTA CRUZ'),
                ('RECUPERADOS',            'SANTA FE'),
                ('RECUPERADOS', 'SANTIAGO DEL ESTERO'),
                ('RECUPERADOS',    'TIERRA DEL FUEGO'),
                ('RECUPERADOS',             'TUCUMAN')],
               names=['TYPE', 'PROVINCIA'])



### Example of use


```python
provinces = api.df_provinces.loc['CONFIRMADOS']['26/03']
provinces = provinces[provinces>0]
provinces.plot.bar()
```




    <matplotlib.axes._subplots.AxesSubplot at 0x7f74a7e672e0>




![png](README_files/README_13_1.png)


## Santa Fe API

Python API for working with Santa Fe (Argentina) COVID data reported.

DataTypes exported:
- CityInfo, COVIDStats namedtuples
- SantaFeAPI class

API methods:
- api.get_stats(date)
- api.get_cities_stats(date)
- api.get_departments_stats(date)
API public properties:
- api.df_info : pandas.DataFrame
- api.df_confirmados : pandas.DataFrame
- api.df_descartados : pandas.DataFrame
- api.df_sospechosos : pandas.DataFrame
- api.city_information : Dict[CityName, CityInfo]
    
Exported functions:
- is_city(str)
- is_deparment(str)
- normalize_str(str)

### Important data types.


```python
from santa_fe_api import *
print('COVIDStats namedtuple:', COVIDStats._fields)
```

    COVIDStats namedtuple: ('date', 'place_name', 'confirmados', 'descartados', 'sospechosos')


## Create api instance passing the working directory 
When load the data the API tells if there are no entries in 'Info' sheet for certain city.


```python
api = SantaFeAPI('./')
```

    Download from google drive...


### <code>get_stats : Date -> [ COVIDStats ]</code> of all places
Date must be expressd in DD/M/YYYY format.


```python
api.get_stats('26/3/2020')[:3]
```




    [COVIDStats(date='26/3/2020', place_name='D_GENERAL LOPEZ', confirmados=1.0, descartados=5.0, sospechosos=4.0),
     COVIDStats(date='26/3/2020', place_name='GALVEZ', confirmados=3.0, descartados=4.0, sospechosos=2.0),
     COVIDStats(date='26/3/2020', place_name='VILLA MUGUETA', confirmados=0.0, descartados=1.0, sospechosos=0.0)]



### <code>get_stats : Date -> [ COVIDStats ]</code> of only cities


```python
api.get_cities_stats('26/3/2020')[:3]
```




    [COVIDStats(date='26/3/2020', place_name='GALVEZ', confirmados=3.0, descartados=4.0, sospechosos=2.0),
     COVIDStats(date='26/3/2020', place_name='VILLA MUGUETA', confirmados=0.0, descartados=1.0, sospechosos=0.0),
     COVIDStats(date='26/3/2020', place_name='VILLA CONSTITUCION', confirmados=1.0, descartados=3.0, sospechosos=1.0)]



### <code>get_stats : Date -> [ COVIDStats ]</code> of only departments


```python
api.get_departments_stats('26/3/2020')[:10]
```




    [COVIDStats(date='26/3/2020', place_name='D_GENERAL LOPEZ', confirmados=1.0, descartados=5.0, sospechosos=4.0),
     COVIDStats(date='26/3/2020', place_name='D_SAN JAVIER', confirmados=1.0, descartados=2.0, sospechosos=0.0),
     COVIDStats(date='26/3/2020', place_name='D_CONSTITUCION', confirmados=1.0, descartados=3.0, sospechosos=1.0),
     COVIDStats(date='26/3/2020', place_name='D_ROSARIO', confirmados=15.0, descartados=88.0, sospechosos=22.0),
     COVIDStats(date='26/3/2020', place_name='D_SAN JERONIMO', confirmados=3.0, descartados=4.0, sospechosos=6.0),
     COVIDStats(date='26/3/2020', place_name='D_CASEROS', confirmados=2.0, descartados=0.0, sospechosos=1.0),
     COVIDStats(date='26/3/2020', place_name='D_GARAY', confirmados=2.0, descartados=2.0, sospechosos=5.0),
     COVIDStats(date='26/3/2020', place_name='D_SAN MARTIN', confirmados=0.0, descartados=3.0, sospechosos=0.0),
     COVIDStats(date='26/3/2020', place_name='D_LAS COLONIAS', confirmados=3.0, descartados=2.0, sospechosos=3.0),
     COVIDStats(date='26/3/2020', place_name='D_LA CAPITAL', confirmados=18.0, descartados=38.0, sospechosos=22.0)]



### Exported DataFrames
Also exports 3 pandas.DataFrame <code>df_confirmados, df_descartados, df_sospechosos</code>.

With the content of Google Drive base 'Confirmados', 'Descartados', 'Sospechos'.

Values are cumulative. City names are normalized using normalize_str function.


```python
api.df_confirmados.head(3)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>14/3/2020</th>
      <th>15/3/2020</th>
      <th>16/3/2020</th>
      <th>17/3/2020</th>
      <th>18/3/2020</th>
      <th>19/3/2020</th>
      <th>20/3/2020</th>
      <th>21/3/2020</th>
      <th>22/3/2020</th>
      <th>23/3/2020</th>
      <th>...</th>
      <th>25/3/2020</th>
      <th>26/3/2020</th>
      <th>27/3/2020</th>
      <th>28/3/2020</th>
      <th>29/3/2020</th>
      <th>30/3/2020</th>
      <th>31/3/2020</th>
      <th>1/4/2020</th>
      <th>2/4/2020</th>
      <th>3/4/2020</th>
    </tr>
    <tr>
      <th>PLACE</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>TOTAL</th>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>2.0</td>
      <td>2.0</td>
      <td>4.0</td>
      <td>4.0</td>
      <td>15.0</td>
      <td>...</td>
      <td>39.0</td>
      <td>55.0</td>
      <td>64.0</td>
      <td>77.0</td>
      <td>90.0</td>
      <td>111.0</td>
      <td>133.0</td>
      <td>144.0</td>
      <td>152.0</td>
      <td>160.0</td>
    </tr>
    <tr>
      <th>D_9 DE JULIO</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>TOSTADO</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>3 rows × 21 columns</p>
</div>




```python
api.df_descartados.head(3)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>14/3/2020</th>
      <th>15/3/2020</th>
      <th>16/3/2020</th>
      <th>17/3/2020</th>
      <th>18/3/2020</th>
      <th>19/3/2020</th>
      <th>20/3/2020</th>
      <th>21/3/2020</th>
      <th>22/3/2020</th>
      <th>23/3/2020</th>
      <th>...</th>
      <th>25/3/2020</th>
      <th>26/3/2020</th>
      <th>27/3/2020</th>
      <th>28/3/2020</th>
      <th>29/3/2020</th>
      <th>30/3/2020</th>
      <th>31/3/2020</th>
      <th>1/4/2020</th>
      <th>2/4/2020</th>
      <th>3/4/2020</th>
    </tr>
    <tr>
      <th>PLACE</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>TOTAL</th>
      <td>18.0</td>
      <td>21.0</td>
      <td>22.0</td>
      <td>25.0</td>
      <td>28.0</td>
      <td>38.0</td>
      <td>45.0</td>
      <td>52.0</td>
      <td>59.0</td>
      <td>64.0</td>
      <td>...</td>
      <td>120.0</td>
      <td>161.0</td>
      <td>214.0</td>
      <td>280.0</td>
      <td>332.0</td>
      <td>383.0</td>
      <td>486.0</td>
      <td>538.0</td>
      <td>654.0</td>
      <td>795.0</td>
    </tr>
    <tr>
      <th>D_9 DE JULIO</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>TOSTADO</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
    </tr>
  </tbody>
</table>
<p>3 rows × 21 columns</p>
</div>




```python
api.df_sospechosos.head(3)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>14/3/2020</th>
      <th>15/3/2020</th>
      <th>16/3/2020</th>
      <th>17/3/2020</th>
      <th>18/3/2020</th>
      <th>19/3/2020</th>
      <th>20/3/2020</th>
      <th>21/3/2020</th>
      <th>22/3/2020</th>
      <th>23/3/2020</th>
      <th>...</th>
      <th>25/3/2020</th>
      <th>26/3/2020</th>
      <th>27/3/2020</th>
      <th>28/3/2020</th>
      <th>29/3/2020</th>
      <th>30/3/2020</th>
      <th>31/3/2020</th>
      <th>1/4/2020</th>
      <th>2/4/2020</th>
      <th>3/4/2020</th>
    </tr>
    <tr>
      <th>PLACE</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>TOTAL</th>
      <td>6.0</td>
      <td>10.0</td>
      <td>14.0</td>
      <td>20.0</td>
      <td>42.0</td>
      <td>39.0</td>
      <td>43.0</td>
      <td>56.0</td>
      <td>54.0</td>
      <td>89.0</td>
      <td>...</td>
      <td>72.0</td>
      <td>89.0</td>
      <td>105.0</td>
      <td>87.0</td>
      <td>69.0</td>
      <td>132.0</td>
      <td>116.0</td>
      <td>141.0</td>
      <td>155.0</td>
      <td>136.0</td>
    </tr>
    <tr>
      <th>D_9 DE JULIO</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>TOSTADO</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>3 rows × 21 columns</p>
</div>



### Exported Dict[CityName, DepartmentName]
<code>to_department(str)</code> property stores CityName to DepartmentName assignations.


```python

```

### Example of use

Uses <code>is_city(str)</code> <code>is_deparment(str)</code> method to check if a place name is city or deparment.


```python
ciudades = api.df_confirmados[ api.df_confirmados.index.map(is_city)  ]['26/3/2020']
ciudades = ciudades[ciudades>0]
ciudades.plot.bar()
```




    <matplotlib.axes._subplots.AxesSubplot at 0x7f74a9cad7c0>




![png](README_files/README_32_1.png)

