# Retrasos en Reportes COVID19 de Mininsterio de Salud Argentina

#### Autor: Mariano Crosetti (@mcros22)
##### Agradecimiento a Mauro Infantino (@plenque) cuya recolección de reportes (https://covidstats.com.ar/archivos/) hizo posible este análisis

## Resumen

Analizamos cuantitativamente el retraso que existe en los reportes de diagnósticos Datos Abiertos de Ministerio de Salud (http://datos.salud.gob.ar/dataset/covid-19-casos-registrados-en-la-republica-argentina).

Constatamos que los reportes en las planillas de datos abiertos coinciden con los reportes oficiales dado por canales como twitter (https://twitter.com/msalnacion).

Arrojamos luz acerca del *significado* (cómo deben ser interpretados acorde a estas demoras) de los datos. Creemos que esto puede servir tanto a:
- analistas que se basan en los datos abiertos para hacer gráficas.
- periodistas que hacen notas y reportes con los datos publicados por @msalnacion.
Un análisis o notas periodísticas serias deben tener necesariamente en cuenta esta situación.

Además el presente reporte libera el código con el que se hizo el análisis, constituyendo un experimento *reproducible y auditable* para otros analistas. Pude también ser usado fácilmente para analizar demoras en otros eventos reportados (como por ejemplo internaciones).

Por otro lado pretende hacer un aporte también a los agentes tomadores de decisión pudiendo señalar en que regiones se producen las mayores demoras.

## Desarrollo del trabajo

Diariamente el Ministerio de Salud de la Nación Argentina emite dos informes diarios con nuevos diagnósticos, fallecimientos y otros eventos relacionados a la pandemia de COVID19 en el territorio Argentino.

Además y de hace 15/05 se publican datos abiertos desagregados por casos en http://datos.salud.gob.ar/dataset/covid-19-casos-registrados-en-la-republica-argentina. Publicar datos abiertos es un paso de enorme transparencia y permite la realización de análisis y aportes privados (como el presente).

Muchos de los que analizamos y visualizamos la evolución de los contagios, fallecimientos (y otros eventos como internaciones, uso de respiradores, etc) utilizando los datos abirtos, ya sabemos que existen demoras en la carga de esos eventos. O sea, que en el reporte de un día se reportan diagnósticos, fallecimientos, internaciones de fechas varios días anteriores. Es por eso que muchos optan por no mostrar los valores de los últimos días (como hacemos en https://covidargentina.com.ar/?sec=G) o señalarlos en otro color e indicar que son valores que siguen creciendo (https://twitter.com/mmbarrionuevo/status/1282094493735497729).

Otros, especialmente muchos periodistas analizan de primera mano la información proveída por MinSalud (https://twitter.com/msalnacion). Veremos que los reportes en datos abiertos están tan actualizados como los reportes de sitaución de twitter (por lo cual deducimos que en éstos últimos los contagios, fallecimientos, etc informados respectan a varios días antes). Es por eso que es importante para quién se base o difunda la información de @msalnacion conocer de estas demoras.

El tema de rezasgos en los datos informados se viralizó la semana pasada en los tweets: https://twitter.com/fedetiberti/status/1291803901558247433 y nota de La Nación https://www.lanacion.com.ar/sociedad/coronavirus-uno-cada-cinco-muertes-pais-fueron-nid2415945.
Por un lado la viralización es positiva en el sentido que es correcto que todo aquel que lea, y en especial difunda o visualice datos *debiera* conocer del rezasgo y entender su cuantificación. Por el otro de no ser informada bien sólo ayuda a descreer de cualquier tipo de información oficial lo cuál termina siendo **peligroso**.


```python
%matplotlib inline
%reload_ext autoreload
%autoreload 2
```


```python
from common import *
```

## Preliminar

Para hacer este análisis necesitamos contar con los reportes diarios de TODOS los días (para compararlos y ver cuándo aparecen reportados los eventos por primera vez). Afortunadamente Mauro Infantino (https://twitter.com/plenque) se encargó de ello en https://covidstats.com.ar/archivos/.

Usar las funciones *download_all_csvs()* y *extract_all_tar()* para descargar en *DATA_PATH* los reportes y extraerlos respectivamente.

*Advertencia:*los targz por sí solo ocupan 500 MB y los csv's descomprimidos 10 GB.

## Analizando todos los reportes

A continuación analizamos todos los csv's, filtrando los que clasificacion_resumen==Confirmado y agrupando por fecha_diagnostico (por ahora todos juntos, luego haremos para cada provincia). 
El csv obtenido tiene para cada fecha_diagnostico cuánto fue reportado en cada csv (columna value). Esta función suele demorar por lo cual subí fecha_diagnostico.csv al repo.


```python
history_df = create_history_df(csv_oldest_date='2019',
                               analysed_date_column = 'fecha_diagnostico',
                               locations_columns_hierarchy = [],
                               filter_function = filter_confirmados,
                               verbose=False)
history_df.to_csv('./fecha_diagnostico.csv',index=False)
history_df
```

    /home/marian/anaconda3/lib/python3.7/site-packages/IPython/core/interactiveshell.py:3331: DtypeWarning: Columns (15) have mixed types.Specify dtype option on import or set low_memory=False.
      exec(code_obj, self.user_global_ns, self.user_ns)
    /home/marian/anaconda3/lib/python3.7/site-packages/IPython/core/interactiveshell.py:3331: DtypeWarning: Columns (0) have mixed types.Specify dtype option on import or set low_memory=False.
      exec(code_obj, self.user_global_ns, self.user_ns)





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
      <th>LOCATION</th>
      <th>fecha_diagnostico</th>
      <th>value</th>
      <th>fecha_csv</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>ALL</td>
      <td>2020-03-03</td>
      <td>1</td>
      <td>2020-06-16</td>
    </tr>
    <tr>
      <th>1</th>
      <td>ALL</td>
      <td>2020-03-06</td>
      <td>6</td>
      <td>2020-06-16</td>
    </tr>
    <tr>
      <th>2</th>
      <td>ALL</td>
      <td>2020-03-07</td>
      <td>1</td>
      <td>2020-06-16</td>
    </tr>
    <tr>
      <th>3</th>
      <td>ALL</td>
      <td>2020-03-08</td>
      <td>2</td>
      <td>2020-06-16</td>
    </tr>
    <tr>
      <th>4</th>
      <td>ALL</td>
      <td>2020-03-09</td>
      <td>6</td>
      <td>2020-06-16</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>7042</th>
      <td>ALL</td>
      <td>2020-08-04</td>
      <td>6413</td>
      <td>2020-08-08</td>
    </tr>
    <tr>
      <th>7043</th>
      <td>ALL</td>
      <td>2020-08-05</td>
      <td>6860</td>
      <td>2020-08-08</td>
    </tr>
    <tr>
      <th>7044</th>
      <td>ALL</td>
      <td>2020-08-06</td>
      <td>6184</td>
      <td>2020-08-08</td>
    </tr>
    <tr>
      <th>7045</th>
      <td>ALL</td>
      <td>2020-08-07</td>
      <td>5355</td>
      <td>2020-08-08</td>
    </tr>
    <tr>
      <th>7046</th>
      <td>ALL</td>
      <td>2020-08-08</td>
      <td>1783</td>
      <td>2020-08-08</td>
    </tr>
  </tbody>
</table>
<p>7047 rows × 4 columns</p>
</div>



## Comparando contra twitter 

Antes de analizar las demoras en los datos abiertos obtendremos la diferencia diaria de diagnósticos reportados para algunas fechas y lo compararemos con lo reportado por la cuenta de twitter de 

El código que se encuentra a continuación muestra las diferencias reportadas en diagnósticos diarios. Copiamos aquí los reportas sacados de los cortes diarios de https://twitter.com/msalnacion (los casos nuevos diarios aparecen en varios tweets a lo largo del día y luego hacen un corte y aparece el número del día siguiente).

2020-08-01 5929\
2020-08-02 5241\
2020-08-03 5376\
2020-08-04 4824\
2020-08-05 6792

Vemos que los números no difieren mucho. Salvo el 08-04 y 08-05 (pero si los sumamos dan lo mismo). Probablemnte hayan hecho un corte distinto entre los datos abiertos y el reporte ese día. Pero lo que nos indica este análisis es que se trata de la misma información y que los retrasos que analicemos en los datos abiertos también existen en los datos anunciados en @msalnacion (y por ende los que ponen en las noticias diarios y programas de televisión).


```python
history_df.groupby('fecha_csv')['value'].sum().diff().loc[['2020-08-01','2020-08-02','2020-08-03','2020-08-04','2020-08-05']]
```




    fecha_csv
    2020-08-01     5241.0
    2020-08-02     5372.0
    2020-08-03     4828.0
    2020-08-04    10022.0
    2020-08-05     3917.0
    Name: value, dtype: float64



## Analizando retraso

El código que tenemos a continuación calcula las variaciones diarias reporadas en diferentes días y para cada una el delay en días que tardaron esos casos en reportarse para determinada fecha_diagnostico


```python
hdf = pd.read_csv('fecha_diagnostico.csv')

analysed_date_column = [c for c in hdf.columns if c not in ['LOCATION', 'fecha_csv', 'value']][0]

hdf = format_history_df(hdf, analysed_date_column)
hdf.set_index(['LOCATION','fecha_diagnostico','fecha_csv']).sort_index()
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
      <th></th>
      <th>value</th>
      <th>value_diff</th>
      <th>delay</th>
      <th>weighted_delay</th>
      <th>value_ratio</th>
    </tr>
    <tr>
      <th>LOCATION</th>
      <th>fecha_diagnostico</th>
      <th>fecha_csv</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="11" valign="top">ALL</th>
      <th rowspan="5" valign="top">2020-06-16</th>
      <th>2020-06-16</th>
      <td>513</td>
      <td>513.0</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.309222</td>
    </tr>
    <tr>
      <th>2020-06-17</th>
      <td>1229</td>
      <td>716.0</td>
      <td>1</td>
      <td>716.0</td>
      <td>0.740808</td>
    </tr>
    <tr>
      <th>2020-06-18</th>
      <td>1517</td>
      <td>288.0</td>
      <td>2</td>
      <td>576.0</td>
      <td>0.914406</td>
    </tr>
    <tr>
      <th>2020-06-19</th>
      <td>1586</td>
      <td>69.0</td>
      <td>3</td>
      <td>207.0</td>
      <td>0.955998</td>
    </tr>
    <tr>
      <th>2020-06-20</th>
      <td>1599</td>
      <td>13.0</td>
      <td>4</td>
      <td>52.0</td>
      <td>0.963834</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">2020-08-06</th>
      <th>2020-08-07</th>
      <td>5560</td>
      <td>3116.0</td>
      <td>1</td>
      <td>3116.0</td>
      <td>0.899094</td>
    </tr>
    <tr>
      <th>2020-08-08</th>
      <td>6184</td>
      <td>624.0</td>
      <td>2</td>
      <td>1248.0</td>
      <td>1.000000</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">2020-08-07</th>
      <th>2020-08-07</th>
      <td>2435</td>
      <td>2435.0</td>
      <td>0</td>
      <td>0.0</td>
      <td>0.454715</td>
    </tr>
    <tr>
      <th>2020-08-08</th>
      <td>5355</td>
      <td>2920.0</td>
      <td>1</td>
      <td>2920.0</td>
      <td>1.000000</td>
    </tr>
    <tr>
      <th>2020-08-08</th>
      <th>2020-08-08</th>
      <td>1783</td>
      <td>1783.0</td>
      <td>0</td>
      <td>0.0</td>
      <td>1.000000</td>
    </tr>
  </tbody>
</table>
<p>1484 rows × 5 columns</p>
</div>



Con esta información se puede extraer para cada fecha_diagnostico métricas acerca de su retraso. A continuación vemos el promedio de retraso que tenemos *actualmente* para cada fecha_diagnostico.

Notar que nos referimos a *actualmente* porque sobre los últimos días es probable que en los futuros reportes sean reportados casos con fechas_diagnosticos para esos días por lo cual el retraso promedio de esos días todavía es suceptible de seguir creciendo.


```python
expected_delay(hdf,analysed_date_column).iloc[-30:-7]
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
      <th>expected_delay</th>
    </tr>
    <tr>
      <th>LOCATION</th>
      <th>fecha_diagnostico</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="23" valign="top">ALL</th>
      <th>2020-07-10</th>
      <td>1.587823</td>
    </tr>
    <tr>
      <th>2020-07-11</th>
      <td>1.821985</td>
    </tr>
    <tr>
      <th>2020-07-12</th>
      <td>1.427035</td>
    </tr>
    <tr>
      <th>2020-07-13</th>
      <td>1.459095</td>
    </tr>
    <tr>
      <th>2020-07-14</th>
      <td>1.699181</td>
    </tr>
    <tr>
      <th>2020-07-15</th>
      <td>1.569508</td>
    </tr>
    <tr>
      <th>2020-07-16</th>
      <td>1.832780</td>
    </tr>
    <tr>
      <th>2020-07-17</th>
      <td>1.963559</td>
    </tr>
    <tr>
      <th>2020-07-18</th>
      <td>2.227987</td>
    </tr>
    <tr>
      <th>2020-07-19</th>
      <td>1.562890</td>
    </tr>
    <tr>
      <th>2020-07-20</th>
      <td>1.715105</td>
    </tr>
    <tr>
      <th>2020-07-21</th>
      <td>1.541652</td>
    </tr>
    <tr>
      <th>2020-07-22</th>
      <td>1.523942</td>
    </tr>
    <tr>
      <th>2020-07-23</th>
      <td>1.389015</td>
    </tr>
    <tr>
      <th>2020-07-24</th>
      <td>1.512690</td>
    </tr>
    <tr>
      <th>2020-07-25</th>
      <td>1.352828</td>
    </tr>
    <tr>
      <th>2020-07-26</th>
      <td>1.472389</td>
    </tr>
    <tr>
      <th>2020-07-27</th>
      <td>1.296533</td>
    </tr>
    <tr>
      <th>2020-07-28</th>
      <td>1.510120</td>
    </tr>
    <tr>
      <th>2020-07-29</th>
      <td>1.425182</td>
    </tr>
    <tr>
      <th>2020-07-30</th>
      <td>1.208362</td>
    </tr>
    <tr>
      <th>2020-07-31</th>
      <td>1.383456</td>
    </tr>
    <tr>
      <th>2020-08-01</th>
      <td>1.233400</td>
    </tr>
  </tbody>
</table>
</div>



Si bien se calculo el retraso promedio para mostrar lo que podíamos hacer con los datos no creemos recomendable fijarnos en esta medida a la hora de analizar *estos* datos.

Esto es debido a que la distribución es claramente no normal y no nos dice mucho la media, ni la varianza, ya que son indicadores no robustos (un outliers suficientemente grande puede aumentar la media y varianza arbitrariamente). A continuación mostramos una gráfica de los valores de value_diff para ciertas fechas_diagnosticos en función al delay para observar las distribuciones.


```python
hdf_toplot = hdf[(hdf['fecha_diagnostico']>='2020-07-20') & (hdf['fecha_diagnostico']<'2020-08-01')]
plot_df = hdf_toplot.pivot(index='delay', columns='fecha_diagnostico', values='value_diff')
display(plot_df)
plot_df.fillna(0).plot(figsize=(20,20))
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
      <th>fecha_diagnostico</th>
      <th>2020-07-20</th>
      <th>2020-07-21</th>
      <th>2020-07-22</th>
      <th>2020-07-23</th>
      <th>2020-07-24</th>
      <th>2020-07-25</th>
      <th>2020-07-26</th>
      <th>2020-07-27</th>
      <th>2020-07-28</th>
      <th>2020-07-29</th>
      <th>2020-07-30</th>
      <th>2020-07-31</th>
    </tr>
    <tr>
      <th>delay</th>
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
      <th>0</th>
      <td>637.0</td>
      <td>1659.0</td>
      <td>1760.0</td>
      <td>2025.0</td>
      <td>2016.0</td>
      <td>1464.0</td>
      <td>1011.0</td>
      <td>1602.0</td>
      <td>1973.0</td>
      <td>1898.0</td>
      <td>1926.0</td>
      <td>2022.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2777.0</td>
      <td>2685.0</td>
      <td>2544.0</td>
      <td>2267.0</td>
      <td>2326.0</td>
      <td>2000.0</td>
      <td>1381.0</td>
      <td>2463.0</td>
      <td>2302.0</td>
      <td>3002.0</td>
      <td>2713.0</td>
      <td>2444.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>536.0</td>
      <td>600.0</td>
      <td>698.0</td>
      <td>455.0</td>
      <td>616.0</td>
      <td>485.0</td>
      <td>432.0</td>
      <td>441.0</td>
      <td>634.0</td>
      <td>387.0</td>
      <td>562.0</td>
      <td>1335.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>229.0</td>
      <td>149.0</td>
      <td>206.0</td>
      <td>303.0</td>
      <td>399.0</td>
      <td>352.0</td>
      <td>218.0</td>
      <td>145.0</td>
      <td>213.0</td>
      <td>150.0</td>
      <td>211.0</td>
      <td>349.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>135.0</td>
      <td>63.0</td>
      <td>52.0</td>
      <td>224.0</td>
      <td>240.0</td>
      <td>145.0</td>
      <td>83.0</td>
      <td>241.0</td>
      <td>88.0</td>
      <td>179.0</td>
      <td>187.0</td>
      <td>377.0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>111.0</td>
      <td>42.0</td>
      <td>67.0</td>
      <td>187.0</td>
      <td>123.0</td>
      <td>29.0</td>
      <td>17.0</td>
      <td>78.0</td>
      <td>51.0</td>
      <td>128.0</td>
      <td>122.0</td>
      <td>23.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>43.0</td>
      <td>54.0</td>
      <td>176.0</td>
      <td>73.0</td>
      <td>178.0</td>
      <td>69.0</td>
      <td>43.0</td>
      <td>36.0</td>
      <td>232.0</td>
      <td>198.0</td>
      <td>66.0</td>
      <td>57.0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>46.0</td>
      <td>124.0</td>
      <td>49.0</td>
      <td>93.0</td>
      <td>89.0</td>
      <td>48.0</td>
      <td>4.0</td>
      <td>11.0</td>
      <td>193.0</td>
      <td>68.0</td>
      <td>67.0</td>
      <td>64.0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>17.0</td>
      <td>79.0</td>
      <td>91.0</td>
      <td>61.0</td>
      <td>27.0</td>
      <td>35.0</td>
      <td>20.0</td>
      <td>99.0</td>
      <td>85.0</td>
      <td>91.0</td>
      <td>40.0</td>
      <td>99.0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>85.0</td>
      <td>42.0</td>
      <td>9.0</td>
      <td>28.0</td>
      <td>30.0</td>
      <td>37.0</td>
      <td>104.0</td>
      <td>16.0</td>
      <td>31.0</td>
      <td>85.0</td>
      <td>14.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>10</th>
      <td>78.0</td>
      <td>34.0</td>
      <td>41.0</td>
      <td>7.0</td>
      <td>4.0</td>
      <td>14.0</td>
      <td>8.0</td>
      <td>13.0</td>
      <td>22.0</td>
      <td>9.0</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>11</th>
      <td>4.0</td>
      <td>65.0</td>
      <td>5.0</td>
      <td>2.0</td>
      <td>40.0</td>
      <td>3.0</td>
      <td>5.0</td>
      <td>15.0</td>
      <td>6.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>12</th>
      <td>3.0</td>
      <td>-1.0</td>
      <td>1.0</td>
      <td>5.0</td>
      <td>6.0</td>
      <td>1.0</td>
      <td>5.0</td>
      <td>3.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>13</th>
      <td>1.0</td>
      <td>23.0</td>
      <td>3.0</td>
      <td>3.0</td>
      <td>5.0</td>
      <td>3.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>14</th>
      <td>-1.0</td>
      <td>18.0</td>
      <td>15.0</td>
      <td>1.0</td>
      <td>6.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>15</th>
      <td>3.0</td>
      <td>-1.0</td>
      <td>18.0</td>
      <td>1.0</td>
      <td>2.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>16</th>
      <td>-1.0</td>
      <td>1.0</td>
      <td>14.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>17</th>
      <td>1.0</td>
      <td>1.0</td>
      <td>15.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>18</th>
      <td>1.0</td>
      <td>5.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>19</th>
      <td>2.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>





    <matplotlib.axes._subplots.AxesSubplot at 0x7fe9cf48da10>




![png](Retrasos%20en%20Reportes%20COVID19%20de%20MinSalud_files/Retrasos%20en%20Reportes%20COVID19%20de%20MinSalud_12_2.png)


### Medidas robustas

Una medida más significativa y robusta podría ser la mediana (sabemos que el 50% de los eventos reportados fueron reportados antes de cierto número de días). U otra medida del estilo como los cuartiles o percentiles. Actualmente tomamos el percentil 90: sabemos que se han reportado el 90% de los casos con hasta cierta cantidad de días de retraso. A continuación para cada fecha_diagnóstico:


```python
delay_to_confident(hdf,'fecha_diagnostico',0.90).set_index(['LOCATION','fecha_diagnostico']).sort_index()
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
      <th>delay</th>
    </tr>
    <tr>
      <th>LOCATION</th>
      <th>fecha_diagnostico</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="54" valign="top">ALL</th>
      <th>2020-06-16</th>
      <td>2</td>
    </tr>
    <tr>
      <th>2020-06-17</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-18</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-06-19</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-20</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-21</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-22</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-23</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-24</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-25</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-26</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-27</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-06-28</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-06-29</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-30</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-01</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-02</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-03</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-04</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-05</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-06</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-07</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-08</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-09</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-10</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-11</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-12</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-13</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-14</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-15</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-16</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-17</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-18</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-19</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-20</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-21</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-22</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-23</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-24</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-25</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-26</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-27</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-28</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-29</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-30</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-31</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-08-01</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-08-02</th>
      <td>2</td>
    </tr>
    <tr>
      <th>2020-08-03</th>
      <td>2</td>
    </tr>
    <tr>
      <th>2020-08-04</th>
      <td>2</td>
    </tr>
    <tr>
      <th>2020-08-05</th>
      <td>2</td>
    </tr>
    <tr>
      <th>2020-08-06</th>
      <td>2</td>
    </tr>
    <tr>
      <th>2020-08-07</th>
      <td>1</td>
    </tr>
    <tr>
      <th>2020-08-08</th>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



### Limitaciones y asumciones

Primero que nada cabe aclarar que nos basamos en que las curvas tienen un tendencia y no van a aparecer en el *futuro lejano* muchos reportados para cierta fecha. Sino cualquier indicador que evaluemos sobre ella no tendría sentido.

Por el otro lado hay que reconocer que existe una incapacidad intrínseca para tener un muestreo representativo las distribciones que queremos. Nosotros queremos dada una fecha de diagnóstico, la distribución de casos reportados en función a su retraso. Cómo pueden seguir apareciendo observaciones en el futuro, hay una limitación intrínseca de que nuestra muestra sea representativa. Tenemos una muestra absoluta para los retrasos que ya ocurrieron y no sabemos como serán los retrasos que no ocurrieron

Por eso vamos a trabajar con los retrasos acumulados: para cada fecha se considerará los casos reportados para esa fecha o *fechas anteriores* y para todos esos casos se tendrá en cuanta su retraso (diferencia entre fecha cuando fue reportada y fecha del diagnostico).

## Indicador elegido

Sería bueno dar con un solo indicador para medir el retraso. De manera que sea fácil de comunicar, incorporar a nuestras graficas (por ejemplo sacando los últimos n días) o comparar demoras de diferentes zonas.

Es necesario que dicho indicador sea en la medida posible pesimista. O sea que si sacamos n dias de nuestras gráficas, las barras respectiva a fechas que *no sacamos* no crezcan demasiado en un futuro.

Para ello vamos a tomar los retrasos acumulados que se explicó en la sección anterior y nos extenderemos en el tiempo el retraso del percentil 95 sea menor que la diferencia entre la fecha y la del ultimo reporte que disponemos. Tomaremos el percentil 90 de los retrasos en este rango de fechas considerada como indicador. Fechas posteriores las descartaremos por considerarlas poco representativas de lo que puede ocurrir en un futuro.


```python
chdf = history_df_cumulative(hdf,analysed_date_column)
chdf.set_index(['LOCATION',analysed_date_column, 'delay'])
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
      <th></th>
      <th>value_diff</th>
      <th>value</th>
      <th>value_ratio</th>
      <th>weighted_delay</th>
    </tr>
    <tr>
      <th>LOCATION</th>
      <th>fecha_diagnostico</th>
      <th>delay</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="11" valign="top">ALL</th>
      <th rowspan="5" valign="top">2020-06-16</th>
      <th>0</th>
      <td>513.0</td>
      <td>513.0</td>
      <td>0.309222</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>716.0</td>
      <td>1229.0</td>
      <td>0.740808</td>
      <td>716.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>288.0</td>
      <td>1517.0</td>
      <td>0.914406</td>
      <td>576.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>69.0</td>
      <td>1586.0</td>
      <td>0.955998</td>
      <td>207.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>13.0</td>
      <td>1599.0</td>
      <td>0.963834</td>
      <td>52.0</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">2020-08-08</th>
      <th>49</th>
      <td>0.0</td>
      <td>207508.0</td>
      <td>1.000000</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>50</th>
      <td>0.0</td>
      <td>207508.0</td>
      <td>1.000000</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>51</th>
      <td>0.0</td>
      <td>207508.0</td>
      <td>1.000000</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>52</th>
      <td>0.0</td>
      <td>207508.0</td>
      <td>1.000000</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>53</th>
      <td>0.0</td>
      <td>207508.0</td>
      <td>1.000000</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>2916 rows × 4 columns</p>
</div>




```python
delay_to_confident(chdf,'fecha_diagnostico',0.95).set_index(['LOCATION','fecha_diagnostico']).sort_index()
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
      <th>delay</th>
    </tr>
    <tr>
      <th>LOCATION</th>
      <th>fecha_diagnostico</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="54" valign="top">ALL</th>
      <th>2020-06-16</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-17</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-18</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-19</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-20</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-21</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-22</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-23</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-24</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-25</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-26</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-27</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-28</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-29</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-06-30</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-01</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-02</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-03</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-04</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-05</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-07-06</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-07</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-08</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-09</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-10</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-11</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-12</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-13</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-14</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-15</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-16</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-17</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-18</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-19</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-20</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-21</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-22</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-23</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-24</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-25</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-26</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-27</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-28</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-29</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-30</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-07-31</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-08-01</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-08-02</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-08-03</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-08-04</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-08-05</th>
      <td>6</td>
    </tr>
    <tr>
      <th>2020-08-06</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-08-07</th>
      <td>5</td>
    </tr>
    <tr>
      <th>2020-08-08</th>
      <td>5</td>
    </tr>
  </tbody>
</table>
</div>




```python
delay_to_confident(chdf,'fecha_diagnostico',0.90).set_index(['LOCATION','fecha_diagnostico']).sort_index()
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
      <th>delay</th>
    </tr>
    <tr>
      <th>LOCATION</th>
      <th>fecha_diagnostico</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="54" valign="top">ALL</th>
      <th>2020-06-16</th>
      <td>2</td>
    </tr>
    <tr>
      <th>2020-06-17</th>
      <td>2</td>
    </tr>
    <tr>
      <th>2020-06-18</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-19</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-06-20</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-06-21</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-06-22</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-06-23</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-24</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-25</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-26</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-27</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-28</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-29</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-06-30</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-01</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-07-02</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-03</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-04</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-05</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-06</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-07</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-08</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-09</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-10</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-11</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-12</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-13</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-14</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-15</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-16</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-17</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-18</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-19</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-20</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-21</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-22</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-23</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-24</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-25</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-26</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-27</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-28</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-29</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-30</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-07-31</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-08-01</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-08-02</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-08-03</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-08-04</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-08-05</th>
      <td>4</td>
    </tr>
    <tr>
      <th>2020-08-06</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-08-07</th>
      <td>3</td>
    </tr>
    <tr>
      <th>2020-08-08</th>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>



Hicimos una función para calcular el indicador elegido que nos devuelve la cantidad de días de delay tras los cuales la fecha analizada no crecerá considerablemente. Además calcula la ultima fecha usada como confiable para calcular dicho indicador.


```python
delay_indicator(chdf,'fecha_diagnostico')
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
      <th>LOCATION</th>
      <th>fecha_diagnostico</th>
      <th>delay</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>ALL</td>
      <td>2020-08-02</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>



# Demoras por region

Volvemos a analizar las demoras en diagnósticos, ahora por región. Esto puede permitir encontrar que región está causando las demoras y permitiría a las autoridades competente resolver los cuellos de botella en el sistema de diagnóstico y carga de datos


```python
history_df = create_history_df(csv_oldest_date='2019',
                               analysed_date_column = 'fecha_diagnostico',
                               locations_columns_hierarchy = ['carga_provincia_nombre'],
                               filter_function = filter_confirmados,
                               verbose=False)
history_df.to_csv('./fecha_diagnostico_region.csv',index=False)
```

    /home/marian/anaconda3/lib/python3.7/site-packages/IPython/core/interactiveshell.py:3331: DtypeWarning: Columns (15) have mixed types.Specify dtype option on import or set low_memory=False.
      exec(code_obj, self.user_global_ns, self.user_ns)
    /home/marian/anaconda3/lib/python3.7/site-packages/IPython/core/interactiveshell.py:3331: DtypeWarning: Columns (0) have mixed types.Specify dtype option on import or set low_memory=False.
      exec(code_obj, self.user_global_ns, self.user_ns)



```python
historic_csv = './fecha_diagnostico_region.csv'
hdf = pd.read_csv(historic_csv)
analysed_date_column = [c for c in history_df.columns if c not in ['LOCATION', 'fecha_csv', 'value']][0]
hdf = format_history_df(hdf, analysed_date_column)
chdf = history_df_cumulative(hdf,analysed_date_column)
indicator = delay_indicator(chdf,analysed_date_column)

```


```python
indicator.sort_values('delay',ascending=False)
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
      <th>LOCATION</th>
      <th>fecha_diagnostico</th>
      <th>delay</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>17</th>
      <td>ALL/San Juan</td>
      <td>2020-07-31</td>
      <td>6</td>
    </tr>
    <tr>
      <th>9</th>
      <td>ALL/Jujuy</td>
      <td>2020-08-02</td>
      <td>5</td>
    </tr>
    <tr>
      <th>1</th>
      <td>ALL/CABA</td>
      <td>2020-08-01</td>
      <td>5</td>
    </tr>
    <tr>
      <th>0</th>
      <td>ALL/Buenos Aires</td>
      <td>2020-08-03</td>
      <td>3</td>
    </tr>
    <tr>
      <th>16</th>
      <td>ALL/Salta</td>
      <td>2020-07-28</td>
      <td>3</td>
    </tr>
    <tr>
      <th>4</th>
      <td>ALL/Chubut</td>
      <td>2020-08-06</td>
      <td>2</td>
    </tr>
    <tr>
      <th>5</th>
      <td>ALL/Corrientes</td>
      <td>2020-08-06</td>
      <td>2</td>
    </tr>
    <tr>
      <th>6</th>
      <td>ALL/Córdoba</td>
      <td>2020-08-06</td>
      <td>2</td>
    </tr>
    <tr>
      <th>8</th>
      <td>ALL/Formosa</td>
      <td>2020-08-01</td>
      <td>2</td>
    </tr>
    <tr>
      <th>10</th>
      <td>ALL/La Pampa</td>
      <td>2020-08-04</td>
      <td>2</td>
    </tr>
    <tr>
      <th>11</th>
      <td>ALL/La Rioja</td>
      <td>2020-08-06</td>
      <td>2</td>
    </tr>
    <tr>
      <th>19</th>
      <td>ALL/Santa Cruz</td>
      <td>2020-08-04</td>
      <td>2</td>
    </tr>
    <tr>
      <th>22</th>
      <td>ALL/Tierra del Fuego</td>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>21</th>
      <td>ALL/Santiago del Estero</td>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>20</th>
      <td>ALL/Santa Fe</td>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>12</th>
      <td>ALL/Mendoza</td>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>15</th>
      <td>ALL/Río Negro</td>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>14</th>
      <td>ALL/Neuquén</td>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>13</th>
      <td>ALL/Misiones</td>
      <td>2020-07-30</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>ALL/Chaco</td>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>ALL/Catamarca</td>
      <td>2020-07-28</td>
      <td>1</td>
    </tr>
    <tr>
      <th>23</th>
      <td>ALL/Tucumán</td>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>18</th>
      <td>ALL/San Luis</td>
      <td>2020-08-01</td>
      <td>0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>ALL/Entre Ríos</td>
      <td>2020-08-07</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



# Demoras en la fecha de fallecimientos

Similarmente y muy facilmente podemos analizar otros rezasgos, por ejemplo en el reporte de fallecimientos.
Claramente aquí hay una demora más severa, aunque también se puede deber a que al haber un menor número de fallecimientos algunos outliers tienen mucho peso.

Aplicar nuestro indicador deja de tener sentido ya que existieron en el pasado demoras considerables que hacen que sólo quiera considerar hasta el 2020-06-25. Requiere un analisis manual (por ejemplo del tercer cuartil).
Aparentemente hubo demoras considerable, especialmente a mediados de julio.


```python
history_df = create_history_df(csv_oldest_date='2019',
                               analysed_date_column = 'fecha_fallecimiento',
                               locations_columns_hierarchy = ['residencia_departamento_nombre'],
                               filter_function = filter_fallecidos,
                               verbose=False)
history_df.to_csv('./fecha_fallecimiento_region_dep.csv',index=False)
```


```python
historic_csv = './fecha_fallecimiento_region.csv'
hdf = pd.read_csv(historic_csv)
analysed_date_column = [c for c in hdf.columns if c not in ['LOCATION', 'fecha_csv', 'value']][0]
hdf = format_history_df(hdf, analysed_date_column)
chdf = history_df_cumulative(hdf,analysed_date_column)
indicator = delay_indicator(chdf,analysed_date_column)

```

# Demoras en la fecha inicio sintomas

Esta fecha al ser anterior a la de diagnóstico presenta mas retraso. Es intersante saber cuanto para incoporar en las gráficas de evolución que hagaos


```python
history_df = create_history_df(csv_oldest_date='2019',
                               analysed_date_column = 'fecha_diagnostico',
                               locations_columns_hierarchy = [],
                               filter_function = filter_confirmados_con_fis,
                               verbose=False)
history_df.to_csv('./fecha_inicio_sintomas.csv',index=False)
```


```python
historic_csv = './fecha_inicio_sintomas.csv'
hdf = pd.read_csv(historic_csv)
analysed_date_column = [c for c in hdf.columns if c not in ['LOCATION', 'fecha_csv', 'value']][0]
hdf = format_history_df(hdf, analysed_date_column)
chdf = history_df_cumulative(hdf,analysed_date_column)
indicator = delay_indicator(chdf,analysed_date_column,p1=0.9,p2=0.5)

```


```python
indicator.sort_values('delay', ascending=False)
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
      <th>LOCATION</th>
      <th>fecha_inicio_sintomas</th>
      <th>delay</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>ALL</td>
      <td>2020-07-26</td>
      <td>6</td>
    </tr>
  </tbody>
</table>
</div>



# Demoras en la fecha cuidados intensivos



```python
history_df = create_history_df(csv_oldest_date='2019',
                               analysed_date_column = 'fecha_cui_intensivo',
                               locations_columns_hierarchy = ['carga_provincia_nombre'],
                               filter_function = filter_uci,
                               verbose=False)
history_df.to_csv('./fecha_cui_intensivo_region.csv',index=False)
```

    /home/marian/anaconda3/lib/python3.7/site-packages/IPython/core/interactiveshell.py:3331: DtypeWarning: Columns (15) have mixed types.Specify dtype option on import or set low_memory=False.
      exec(code_obj, self.user_global_ns, self.user_ns)
    /home/marian/anaconda3/lib/python3.7/site-packages/IPython/core/interactiveshell.py:3331: DtypeWarning: Columns (0) have mixed types.Specify dtype option on import or set low_memory=False.
      exec(code_obj, self.user_global_ns, self.user_ns)



```python
historic_csv = './fecha_cui_intensivo.csv'
hdf = pd.read_csv(historic_csv)
analysed_date_column = [c for c in hdf.columns if c not in ['LOCATION', 'fecha_csv', 'value']][0]
hdf = format_history_df(hdf, analysed_date_column)
chdf = history_df_cumulative(hdf,analysed_date_column)
indicator = delay_indicator(chdf,analysed_date_column)
indicator.sort_values('delay', ascending=False)
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
      <th>LOCATION</th>
      <th>fecha_cui_intensivo</th>
      <th>delay</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>ALL</td>
      <td>2020-07-08</td>
      <td>25</td>
    </tr>
  </tbody>
</table>
</div>




```python
delay_to_confident(chdf,analysed_date_column,0.5)
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
      <th>LOCATION</th>
      <th>fecha_cui_intensivo</th>
      <th>delay</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>ALL</td>
      <td>2020-06-16</td>
      <td>5</td>
    </tr>
    <tr>
      <th>1</th>
      <td>ALL</td>
      <td>2020-06-17</td>
      <td>6</td>
    </tr>
    <tr>
      <th>2</th>
      <td>ALL</td>
      <td>2020-06-18</td>
      <td>5</td>
    </tr>
    <tr>
      <th>3</th>
      <td>ALL</td>
      <td>2020-06-19</td>
      <td>5</td>
    </tr>
    <tr>
      <th>4</th>
      <td>ALL</td>
      <td>2020-06-20</td>
      <td>5</td>
    </tr>
    <tr>
      <th>5</th>
      <td>ALL</td>
      <td>2020-06-21</td>
      <td>5</td>
    </tr>
    <tr>
      <th>6</th>
      <td>ALL</td>
      <td>2020-06-22</td>
      <td>5</td>
    </tr>
    <tr>
      <th>7</th>
      <td>ALL</td>
      <td>2020-06-23</td>
      <td>5</td>
    </tr>
    <tr>
      <th>8</th>
      <td>ALL</td>
      <td>2020-06-24</td>
      <td>4</td>
    </tr>
    <tr>
      <th>9</th>
      <td>ALL</td>
      <td>2020-06-25</td>
      <td>5</td>
    </tr>
    <tr>
      <th>10</th>
      <td>ALL</td>
      <td>2020-06-26</td>
      <td>5</td>
    </tr>
    <tr>
      <th>11</th>
      <td>ALL</td>
      <td>2020-06-27</td>
      <td>4</td>
    </tr>
    <tr>
      <th>12</th>
      <td>ALL</td>
      <td>2020-06-28</td>
      <td>4</td>
    </tr>
    <tr>
      <th>13</th>
      <td>ALL</td>
      <td>2020-06-29</td>
      <td>4</td>
    </tr>
    <tr>
      <th>14</th>
      <td>ALL</td>
      <td>2020-06-30</td>
      <td>4</td>
    </tr>
    <tr>
      <th>15</th>
      <td>ALL</td>
      <td>2020-07-01</td>
      <td>4</td>
    </tr>
    <tr>
      <th>16</th>
      <td>ALL</td>
      <td>2020-07-02</td>
      <td>4</td>
    </tr>
    <tr>
      <th>17</th>
      <td>ALL</td>
      <td>2020-07-03</td>
      <td>4</td>
    </tr>
    <tr>
      <th>18</th>
      <td>ALL</td>
      <td>2020-07-04</td>
      <td>4</td>
    </tr>
    <tr>
      <th>19</th>
      <td>ALL</td>
      <td>2020-07-05</td>
      <td>4</td>
    </tr>
    <tr>
      <th>20</th>
      <td>ALL</td>
      <td>2020-07-06</td>
      <td>4</td>
    </tr>
    <tr>
      <th>21</th>
      <td>ALL</td>
      <td>2020-07-07</td>
      <td>4</td>
    </tr>
    <tr>
      <th>22</th>
      <td>ALL</td>
      <td>2020-07-08</td>
      <td>4</td>
    </tr>
    <tr>
      <th>23</th>
      <td>ALL</td>
      <td>2020-07-09</td>
      <td>4</td>
    </tr>
    <tr>
      <th>24</th>
      <td>ALL</td>
      <td>2020-07-10</td>
      <td>4</td>
    </tr>
    <tr>
      <th>25</th>
      <td>ALL</td>
      <td>2020-07-11</td>
      <td>5</td>
    </tr>
    <tr>
      <th>26</th>
      <td>ALL</td>
      <td>2020-07-12</td>
      <td>4</td>
    </tr>
    <tr>
      <th>27</th>
      <td>ALL</td>
      <td>2020-07-13</td>
      <td>4</td>
    </tr>
    <tr>
      <th>28</th>
      <td>ALL</td>
      <td>2020-07-14</td>
      <td>4</td>
    </tr>
    <tr>
      <th>29</th>
      <td>ALL</td>
      <td>2020-07-15</td>
      <td>4</td>
    </tr>
    <tr>
      <th>30</th>
      <td>ALL</td>
      <td>2020-07-16</td>
      <td>4</td>
    </tr>
    <tr>
      <th>31</th>
      <td>ALL</td>
      <td>2020-07-17</td>
      <td>5</td>
    </tr>
    <tr>
      <th>32</th>
      <td>ALL</td>
      <td>2020-07-18</td>
      <td>5</td>
    </tr>
    <tr>
      <th>33</th>
      <td>ALL</td>
      <td>2020-07-19</td>
      <td>5</td>
    </tr>
    <tr>
      <th>34</th>
      <td>ALL</td>
      <td>2020-07-20</td>
      <td>5</td>
    </tr>
    <tr>
      <th>35</th>
      <td>ALL</td>
      <td>2020-07-21</td>
      <td>4</td>
    </tr>
    <tr>
      <th>36</th>
      <td>ALL</td>
      <td>2020-07-22</td>
      <td>4</td>
    </tr>
    <tr>
      <th>37</th>
      <td>ALL</td>
      <td>2020-07-23</td>
      <td>4</td>
    </tr>
    <tr>
      <th>38</th>
      <td>ALL</td>
      <td>2020-07-24</td>
      <td>4</td>
    </tr>
    <tr>
      <th>39</th>
      <td>ALL</td>
      <td>2020-07-25</td>
      <td>4</td>
    </tr>
    <tr>
      <th>40</th>
      <td>ALL</td>
      <td>2020-07-26</td>
      <td>4</td>
    </tr>
    <tr>
      <th>41</th>
      <td>ALL</td>
      <td>2020-07-27</td>
      <td>4</td>
    </tr>
    <tr>
      <th>42</th>
      <td>ALL</td>
      <td>2020-07-28</td>
      <td>4</td>
    </tr>
    <tr>
      <th>43</th>
      <td>ALL</td>
      <td>2020-07-29</td>
      <td>4</td>
    </tr>
    <tr>
      <th>44</th>
      <td>ALL</td>
      <td>2020-07-30</td>
      <td>4</td>
    </tr>
    <tr>
      <th>45</th>
      <td>ALL</td>
      <td>2020-07-31</td>
      <td>4</td>
    </tr>
    <tr>
      <th>46</th>
      <td>ALL</td>
      <td>2020-08-01</td>
      <td>4</td>
    </tr>
    <tr>
      <th>47</th>
      <td>ALL</td>
      <td>2020-08-02</td>
      <td>4</td>
    </tr>
    <tr>
      <th>48</th>
      <td>ALL</td>
      <td>2020-08-03</td>
      <td>4</td>
    </tr>
    <tr>
      <th>49</th>
      <td>ALL</td>
      <td>2020-08-04</td>
      <td>4</td>
    </tr>
    <tr>
      <th>50</th>
      <td>ALL</td>
      <td>2020-08-05</td>
      <td>4</td>
    </tr>
    <tr>
      <th>51</th>
      <td>ALL</td>
      <td>2020-08-06</td>
      <td>4</td>
    </tr>
    <tr>
      <th>52</th>
      <td>ALL</td>
      <td>2020-08-07</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>



# Grafica


```python
historic_csv = './fecha_diagnostico_region.csv'
#historic_csv = './fecha_fallecimiento_region.csv'
hdf = pd.read_csv(historic_csv)
analysed_date_column = [c for c in hdf.columns if c not in ['LOCATION', 'fecha_csv', 'value']][0]
hdf = format_history_df(hdf, analysed_date_column)
chdf = history_df_cumulative(hdf,analysed_date_column)
```


```python
indicator_fallecimiento = delay_indicator(chdf,analysed_date_column,p1=0.8,p2=0.75).sort_values('delay', ascending=False)
indicator_fallecimiento.set_index('LOCATION')
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
      <th>fecha_fallecimiento</th>
      <th>delay</th>
    </tr>
    <tr>
      <th>LOCATION</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>ALL/Buenos Aires</th>
      <td>2020-07-18</td>
      <td>19</td>
    </tr>
    <tr>
      <th>ALL/Jujuy</th>
      <td>2020-07-19</td>
      <td>16</td>
    </tr>
    <tr>
      <th>ALL/Tierra del Fuego</th>
      <td>2020-07-31</td>
      <td>7</td>
    </tr>
    <tr>
      <th>ALL/Chaco</th>
      <td>2020-07-31</td>
      <td>6</td>
    </tr>
    <tr>
      <th>ALL/Salta</th>
      <td>2020-07-09</td>
      <td>6</td>
    </tr>
    <tr>
      <th>ALL/Corrientes</th>
      <td>2020-07-31</td>
      <td>4</td>
    </tr>
    <tr>
      <th>ALL/CABA</th>
      <td>2020-08-03</td>
      <td>4</td>
    </tr>
    <tr>
      <th>ALL/Santa Fe</th>
      <td>2020-07-31</td>
      <td>3</td>
    </tr>
    <tr>
      <th>ALL/Río Negro</th>
      <td>2020-08-05</td>
      <td>2</td>
    </tr>
    <tr>
      <th>ALL/Santa Cruz</th>
      <td>2020-08-02</td>
      <td>2</td>
    </tr>
    <tr>
      <th>ALL/La Rioja</th>
      <td>2020-08-06</td>
      <td>2</td>
    </tr>
    <tr>
      <th>ALL/Neuquén</th>
      <td>2020-08-06</td>
      <td>2</td>
    </tr>
    <tr>
      <th>ALL/Mendoza</th>
      <td>2020-08-05</td>
      <td>2</td>
    </tr>
    <tr>
      <th>ALL/Córdoba</th>
      <td>2020-08-06</td>
      <td>2</td>
    </tr>
    <tr>
      <th>ALL/Chubut</th>
      <td>2020-07-29</td>
      <td>2</td>
    </tr>
    <tr>
      <th>ALL/Tucumán</th>
      <td>2020-08-04</td>
      <td>2</td>
    </tr>
    <tr>
      <th>ALL/Entre Ríos</th>
      <td>2020-08-05</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>




```python
indicator_diagnostico = delay_indicator(chdf,analysed_date_column,p1=0.9,p2=0.75).sort_values('delay', ascending=False)
indicator_diagnostico.set_index('LOCATION')
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
      <th>fecha_diagnostico</th>
      <th>delay</th>
    </tr>
    <tr>
      <th>LOCATION</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>ALL/San Juan</th>
      <td>2020-07-31</td>
      <td>4</td>
    </tr>
    <tr>
      <th>ALL/Jujuy</th>
      <td>2020-08-03</td>
      <td>4</td>
    </tr>
    <tr>
      <th>ALL/Formosa</th>
      <td>2020-08-01</td>
      <td>2</td>
    </tr>
    <tr>
      <th>ALL/CABA</th>
      <td>2020-08-03</td>
      <td>2</td>
    </tr>
    <tr>
      <th>ALL/Buenos Aires</th>
      <td>2020-08-05</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Misiones</th>
      <td>2020-07-30</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Tierra del Fuego</th>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Santiago del Estero</th>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Santa Fe</th>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Santa Cruz</th>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Salta</th>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Río Negro</th>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Neuquén</th>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Mendoza</th>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/La Rioja</th>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/La Pampa</th>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Córdoba</th>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Corrientes</th>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Chubut</th>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Chaco</th>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Catamarca</th>
      <td>2020-07-28</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Tucumán</th>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>ALL/Entre Ríos</th>
      <td>2020-08-08</td>
      <td>0</td>
    </tr>
    <tr>
      <th>ALL/San Luis</th>
      <td>2020-08-04</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python

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
      <th>LOCATION</th>
      <th>fecha_fallecimiento</th>
      <th>delay_x</th>
      <th>fecha_diagnostico</th>
      <th>delay_y</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>ALL/Buenos Aires</td>
      <td>2020-07-18</td>
      <td>19</td>
      <td>2020-08-05</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>ALL/Jujuy</td>
      <td>2020-07-19</td>
      <td>16</td>
      <td>2020-08-03</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2</th>
      <td>ALL/Tierra del Fuego</td>
      <td>2020-07-31</td>
      <td>7</td>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>ALL/Chaco</td>
      <td>2020-07-31</td>
      <td>6</td>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>ALL/Salta</td>
      <td>2020-07-09</td>
      <td>6</td>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>5</th>
      <td>ALL/Corrientes</td>
      <td>2020-07-31</td>
      <td>4</td>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>6</th>
      <td>ALL/CABA</td>
      <td>2020-08-03</td>
      <td>4</td>
      <td>2020-08-03</td>
      <td>2</td>
    </tr>
    <tr>
      <th>7</th>
      <td>ALL/Santa Fe</td>
      <td>2020-07-31</td>
      <td>3</td>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>8</th>
      <td>ALL/Río Negro</td>
      <td>2020-08-05</td>
      <td>2</td>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>9</th>
      <td>ALL/Santa Cruz</td>
      <td>2020-08-02</td>
      <td>2</td>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>10</th>
      <td>ALL/La Rioja</td>
      <td>2020-08-06</td>
      <td>2</td>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>11</th>
      <td>ALL/Neuquén</td>
      <td>2020-08-06</td>
      <td>2</td>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>12</th>
      <td>ALL/Mendoza</td>
      <td>2020-08-05</td>
      <td>2</td>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>13</th>
      <td>ALL/Córdoba</td>
      <td>2020-08-06</td>
      <td>2</td>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>14</th>
      <td>ALL/Chubut</td>
      <td>2020-07-29</td>
      <td>2</td>
      <td>2020-08-06</td>
      <td>1</td>
    </tr>
    <tr>
      <th>15</th>
      <td>ALL/Tucumán</td>
      <td>2020-08-04</td>
      <td>2</td>
      <td>2020-08-07</td>
      <td>1</td>
    </tr>
    <tr>
      <th>16</th>
      <td>ALL/Entre Ríos</td>
      <td>2020-08-05</td>
      <td>1</td>
      <td>2020-08-08</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python

ax = pd.merge(indicator_fallecimiento,indicator_diagnostico,on='LOCATION').set_index('LOCATION')\
    .rename(columns={
        'delay_x':'25% fallecimiento mas retraso',
        'delay_y':'25% diagnostico mas retraso',}).plot.bar(figsize=(15,15))
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005+0.1))
```


![png](Retrasos%20en%20Reportes%20COVID19%20de%20MinSalud_files/Retrasos%20en%20Reportes%20COVID19%20de%20MinSalud_41_0.png)


## Implicancias - Debo creer en los datos del gobierno?

A raíz de señalar las demoras en los reportes se ha desatado una ola de críticas hacia descreer cualquier información oficial. Esto puede ser **peligroso** dado la cantidad de información no oficial perniciosa que existe.

Con este articulo no pretendemos decirle a nadie lo que quiere creer. Pero hay que subrayar que este análisis (y otros) se *basan* todos en la información de datos abiertos publicado por el Ministerio de Salud. Partiendo desde este punto cualquiera que descrea totalmente de la información del gobierno no debería ni detenerse a leer estos análisis (simplemente sería una pérdida de tiempo).

La disponibilidad de datos abiertos en un gran paso en la transparencia. Del mismo modo lo es la sincronicidad entre los datos que maneja el Ministerio de Salud por canales como twitter y los datos abiertos (están actualizados). Estos permiten a analistas privados hacer análisis como este que pueden ser tomados por los agentes tomadores de decisión a la hora de orientar sus esfuerzos. Debemos colocar los aportes siempre de la crítica constructiva fomentando que se sigan tomando iniciativas de datos abiertos como éstas.

## Conclusiones

- Los reportes diarios de diagnósticos y fallecidos del Ministerio de Salud (@msalnacion) coinciden con los calculados a partir de datos abiertos y por ende se informan casos con el **mismo retraso**.

- **fecha_diagnostico**: el 90% se reporta hasta **4 días** de que ocurre el diagnóstico. Jujuy y CABA lideran este retraso.
- Se reportan considerables retrasos en **fallecimientos**. Entre 10 y 15 días para el 20% de los fallecimientos. Buenos Aires lidera este retraso, le siguen en menor medida Jujuy, Chaco y finalmente CABA.

- **fecha_inicio_sintomas** demora 13 días en alcanzar el 90% de reporte (fechas 13 días sabemos que no aumentarán más del 10% con lo reportado en un futuro) y unos 6 días en tan solo el 50%. Es necesario tener en cuenta si se van a hacer evoluciones por fecha_inicio_sintomas.

- **fecha_cui_intensivo** demora 12 días en alcanzar el 90% de reporte (y el 50% se reporta luego de 4-5 dias)


Es importante saber de los retrasos a diferentes niveles de retraso:

- Periodistas: incluso si comparten los reportes diarios del Ministerio de Salud, es importante que conozcan que esos datos están con atrasos.
- Analistas: para que incorporen estos retrasos en sus visualizaciones (por ejemplo en evoluciones temporales).
- Tomadores de decisión: para que sepan que los retrasos existen, que eventos poseen más o menos retrasos, monitoreen el retraso para verificar que esté en rangos aceptables y sepan de dónde viene el retraso para tomar medidas para mitigarlo.
