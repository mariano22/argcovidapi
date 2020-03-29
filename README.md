# Santa Fe COVID API
Python API for working with Santa Fe (Argentina) COVID data reported

DataTypes exported:
- CityInfo, COVIDStats namedtuples
        > SantaFeAPI class

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
print('CityInfo namedtuple:', CityInfo._fields)
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
    Not info entry for: DESVIO ARIJON
    Not info entry for: CALCHAQUI


### get_stats : Date -> [ COVIDStats ] of all places


```python
api.get_stats('26/3/2020')[:3]
```




    [COVIDStats(date='26/3/2020', place_name='VENADO TUERTO', confirmados=1.0, descartados=3.0, sospechosos=2.0),
     COVIDStats(date='26/3/2020', place_name='CARMEN', confirmados=0.0, descartados=0.0, sospechosos=1.0),
     COVIDStats(date='26/3/2020', place_name='RUFINO', confirmados=0.0, descartados=1.0, sospechosos=0.0)]



### get_stats : Date -> [ COVIDStats ] of only cities


```python
api.get_cities_stats('26/3/2020')[:3]
```




    [COVIDStats(date='26/3/2020', place_name='VENADO TUERTO', confirmados=1.0, descartados=3.0, sospechosos=2.0),
     COVIDStats(date='26/3/2020', place_name='CARMEN', confirmados=0.0, descartados=0.0, sospechosos=1.0),
     COVIDStats(date='26/3/2020', place_name='RUFINO', confirmados=0.0, descartados=1.0, sospechosos=0.0)]



### <code>get_stats : Date -> [ COVIDStats ] of only departments


```python
api.get_departments_stats('26/3/2020')[:10]
```


    ---------------------------------------------------------------------------

    NotImplementedError                       Traceback (most recent call last)

    <ipython-input-51-dfabae7695bd> in <module>
    ----> 1 api.get_departments_stats('26/3/2020')[:10]
    

    ~/Escritorio/corona/map/santafecovidapi/santa_fe_api.py in get_departments_stats(self, date)
         93     def get_departments_stats(self,date):
         94         """ Return a [ COVIDStats ] for the deparments only. """
    ---> 95         raise NotImplementedError
         96         return [ s  for s in self.get_stats(date) if is_deparment(s.place_name) ]
         97 


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

API exports a DataFrame with 'Info' sheet (information about each city).


```python
api.df_info.head(3)
```

API exports a <code>Dict[CityName, CityInfo]</code>


```python
list(api.city_information.items())[:3]
```

Uses <code>is_city(str)</code> <code>is_deparment(str)</code> method to check if a place name is city or deparment.


```python
ciudades = api.df_confirmados[ api.df_confirmados.index.map(is_city)  ]['26/3/2020']
ciudades = ciudades[ciudades>0]
ciudades.plot.bar()
```
