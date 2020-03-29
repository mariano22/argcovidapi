```python
%matplotlib inline
%reload_ext autoreload
%autoreload 2
```


```python
from santa_fe_api import *
""" Important data types. """
print('CityInfo namedtuple:', CityInfo._fields)
print('COVIDStats namedtuple:', COVIDStats._fields)
```

    CityInfo namedtuple: ('latitud', 'longitud', 'departamento')
    COVIDStats namedtuple: ('date', 'place_name', 'confirmados', 'descartados', 'sospechosos')



```python
# Create api instance passing the working directory
api = SantaFeAPI('./', strict_sanity = False)
"""
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
    
    Also see exported functions:
        - is_city(str)
        - is_deparment(str)
        - normalize_str(str)
"""
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





    '\n    API methods:\n        - api.get_stats(date)\n        - api.get_cities_stats(date)\n        - api.get_departments_stats(date)\n    API public properties:\n        - api.df_info : pandas.DataFrame\n        - api.df_confirmados : pandas.DataFrame\n        - api.df_descartados : pandas.DataFrame\n        - api.df_sospechosos : pandas.DataFrame\n        - api.city_information : Dict[CityName, CityInfo]\n    \n    Also see exported functions:\n        - is_city(str)\n        - is_deparment(str)\n        - normalize_str(str)\n'




```python
# get_stats : Date -> [ COVIDStats ] of all places
api.get_stats('26/3/2020')[:3]
```




    [COVIDStats(date='26/3/2020', place_name='VENADO TUERTO', confirmados=1.0, descartados=3.0, sospechosos=2.0),
     COVIDStats(date='26/3/2020', place_name='CARMEN', confirmados=0.0, descartados=0.0, sospechosos=1.0),
     COVIDStats(date='26/3/2020', place_name='RUFINO', confirmados=0.0, descartados=1.0, sospechosos=0.0)]




```python
# get_stats : Date -> [ COVIDStats ] of only cities
api.get_cities_stats('26/3/2020')[:3]
```




    [COVIDStats(date='26/3/2020', place_name='VENADO TUERTO', confirmados=1.0, descartados=3.0, sospechosos=2.0),
     COVIDStats(date='26/3/2020', place_name='CARMEN', confirmados=0.0, descartados=0.0, sospechosos=1.0),
     COVIDStats(date='26/3/2020', place_name='RUFINO', confirmados=0.0, descartados=1.0, sospechosos=0.0)]




```python
# get_stats : Date -> [ COVIDStats ] of only departments
api.get_departments_stats('26/3/2020')[:10]
```


    ---------------------------------------------------------------------------

    NotImplementedError                       Traceback (most recent call last)

    <ipython-input-37-67b0dc858c9b> in <module>
          1 # get_stats : Date -> [ COVIDStats ] of only departments
    ----> 2 api.get_departments_stats('26/3/2020')[:10]
    

    ~/Escritorio/corona/map/santafecovidapi/santa_fe_api.py in get_departments_stats(self, date)
         93     def get_departments_stats(self,date):
         94         """ Return a [ COVIDStats ] for the deparments only. """
    ---> 95         raise NotImplementedError
         96         return [ s  for s in self.get_stats(date) if is_deparment(s.place_name) ]
         97 


    NotImplementedError: 



```python
""" Also exports 3 pandas.DataFrame df_confirmados, df_descartados, df_sospechosos.
    With the content of Google Drive base 'Confirmados', 'Descartados', 'Sospechos'.
    Values are cumulative. City names are normalized using normalize_str function. """
api.df_confirmados.head(3)
```


```python
api.df_descartados.head(3)
```


```python
api.df_sospechosos.head(3)
```


```python
""" Uses is_city(str) is_deparment(str) method to check if a place name is city or deparment. """
ciudades = api.df_confirmados[ api.df_confirmados.index.map(is_city)  ]['26/3/2020']
ciudades = ciudades[ciudades>0]
ciudades.plot.bar()
```


```python
""" API exports a DataFrame with 'Info' sheet (information about each city).  """
api.df_info.head(3)
```


```python
""" API exports a Dict[CityName, CityInfo] """
list(api.city_information.items())[:3]
```
