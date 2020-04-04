# Argentina and Santa Fe COVID API

Based on handed scraped data on goverment reports:
- Argentina: https://docs.google.com/spreadsheets/d/1xDi1RIXFA_cWaKJ-WEBRuFSrHwlFr7308NtQhoBLEsA
- Santa Fe: https://docs.google.com/spreadsheets/d/19aa5sqdsj3nYmBqllPXvgj72cvx63SzB2Hx8B02vMwU

Santa Fe reports are cumulative. National reports shows new daily cases.

We decided to work with cumulatives time series. There is a smart design decision behind that: if we have cumulative confirmed cases, we don't have to read all the entries, only with the frequentcy we are interested in (imagine weekly analysis).

'Sospechosos' could decrease because some cases can move to 'Confirmados' o 'Descartados'.

# Non-Python users

For non python users csv's are generated periodically to be parsed and used (see <code>./csv/ folder</code>). All with cumulative time series.
- For Santa Fe:

<code>csv/SantaFe_Confirmados.csv</code> <code>csv/SantaFe_Sospechosos.csv</code> <code>SantaFe_Descartados.csv</code>

- For Argentina:

<code>csv/Argentina_Tests.csv</code> <code>csv/Argentina_Confirmados.csv</code> <code>csv/Argentina_Fallecidos.csv</code>

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

    COVIDStats namedtuple: ('date', 'place_name', 'confirmados', 'fallecidos')


## Create api instance passing the working directory 
When load the data the API tells if there are no entries in 'Info' sheet for certain city.


```python
api = ArgentinaAPI('./')
```

    Download from google drive...


### <code>get_stats : Date -> [ COVIDStats ]</code> of all provinces


```python
api.get_stats('26/3/2020')[:3]
```


    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    <ipython-input-6-bef93f65c1f4> in <module>
    ----> 1 api.get_stats('26/3/2020')[:3]
    

    ~/Escritorio/covid/argcovidapi/argentina_api.py in get_stats(self, date)
         44         for province_name, r in self.df_confirmados.iterrows():
         45             result.append(COVIDStats(date        = date,
    ---> 46                                      place_name  = province_name,
         47                                      confirmados = self.df_confirmados[date].get(province_name,0),
         48                                      fallecidos = self.df_fallecidos[date].get(province_name,0)))


    NameError: name 'city_name' is not defined


### Exported DataFrames
Also exports 3 pandas.DataFrame <code>df_confirmados, df_fallecidos, df_test</code>.

With the content of Google Drive 'Confirmados_Diff', 'Fallecidos_Diff', 'Test_Diff' but with cumulative values. Provinces names are normalized using normalize_str function.


```python
api.df_confirmados.head(3)
```


```python
api.df_fallecidos.head(3)
```


```python
api.df_test.head(3)
```

### Example of use


```python
provinces = api.df_confirmados['26/3/2020']
provinces = provinces[provinces>0]
provinces.plot.bar()
```

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

    CityInfo namedtuple: ('latitud', 'longitud', 'departamento')
    COVIDStats namedtuple: ('date', 'place_name', 'confirmados', 'descartados', 'sospechosos')


## Create api instance passing the working directory 
When load the data the API tells if there are no entries in 'Info' sheet for certain city.


```python
api = SantaFeAPI('./', strict_sanity = False)
```

    Download from google drive...
    Not info entry for: LAS TOSCAS
    Not info entry for: DESVIO ARIJON
    Not info entry for: CALCHAQUI
    Not info entry for: LAS TOSCAS
    Not info entry for: DESVIO ARIJON
    Not info entry for: CALCHAQUI
    Not info entry for: LAS TOSCAS
    Not info entry for: ESPERANZA
    Not info entry for: DESVIO ARIJON
    Not info entry for: CALCHAQUI


### <code>get_stats : Date -> [ COVIDStats ]</code> of all places


```python
api.get_stats('26/3/2020')[:3]
```




    [COVIDStats(date='26/3/2020', place_name='VENADO TUERTO', confirmados=1.0, descartados=3.0, sospechosos=2.0),
     COVIDStats(date='26/3/2020', place_name='CARMEN', confirmados=0.0, descartados=0.0, sospechosos=1.0),
     COVIDStats(date='26/3/2020', place_name='RUFINO', confirmados=0.0, descartados=1.0, sospechosos=0.0)]



### <code>get_stats : Date -> [ COVIDStats ]</code> of only cities


```python
api.get_cities_stats('26/3/2020')[:3]
```




    [COVIDStats(date='26/3/2020', place_name='VENADO TUERTO', confirmados=1.0, descartados=3.0, sospechosos=2.0),
     COVIDStats(date='26/3/2020', place_name='CARMEN', confirmados=0.0, descartados=0.0, sospechosos=1.0),
     COVIDStats(date='26/3/2020', place_name='RUFINO', confirmados=0.0, descartados=1.0, sospechosos=0.0)]



### <code>get_stats : Date -> [ COVIDStats ]</code> of only departments


```python
api.get_departments_stats('26/3/2020')[:10]
```


    ---------------------------------------------------------------------------

    NotImplementedError                       Traceback (most recent call last)

    <ipython-input-18-dfabae7695bd> in <module>
    ----> 1 api.get_departments_stats('26/3/2020')[:10]
    

    ~/Escritorio/corona/map/santafecovidapi/santa_fe_api.py in get_departments_stats(self, date)
         74     def get_departments_stats(self,date):
         75         """ Return a [ COVIDStats ] for the deparments only. """
    ---> 76         raise NotImplementedError
         77         return [ s  for s in self.get_stats(date) if is_deparment(s.place_name) ]
         78 


    NotImplementedError: 


### Exported DataFrames
Also exports 3 pandas.DataFrame <code>df_confirmados, df_descartados, df_sospechosos</code>.

With the content of Google Drive base 'Confirmados', 'Descartados', 'Sospechos'.

Values are cumulative. City names are normalized using normalize_str function.


```python
api.df_confirmados.head(3)
```


```python
api.df_descartados.head(3)
```


```python
api.df_sospechosos.head(3)
```

### Example of use

Uses <code>is_city(str)</code> <code>is_deparment(str)</code> method to check if a place name is city or deparment.


```python
ciudades = api.df_confirmados[ api.df_confirmados.index.map(is_city)  ]['26/3/2020']
ciudades = ciudades[ciudades>0]
ciudades.plot.bar()
```




    <matplotlib.axes._subplots.AxesSubplot at 0x7f8c2dbe82e0>




![png](README_files/README_30_1.png)

