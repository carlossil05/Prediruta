# PrediRuta

Proyecto aplicado de analítica de datos para analizar la siniestralidad vial en Bogotá y modelar la ocurrencia, el tipo y la severidad de los accidentes.

## Modelo relacional

El modelo original se depuró para conservar solo la información necesaria y evitar columnas repetidas. `ACCIDENTE_ID`, `VEHICULO_ID`, `ACTOR_ID`, `CAUSA_ID` y `CLIMA_ID` permiten relacionar las tablas mediante identificadores enteros.

El modelo final contiene:

- `ACCIDENTE`: fecha, coordenadas, clase y variable objetivo.
- `CLIMA`: observaciones meteorológicas horarias.
- `VIA`: condiciones de la vía asociada al accidente.
- `VEHICULO`: vehículos involucrados.
- `ACTOR_VIAL`: personas involucradas de forma anonimizada.
- `CAUSA`: causas registradas para el accidente.

| Modelo original | Modelo depurado de PrediRuta |
|-----------------| -----------------------------|
| ![Modelo relacional original](data/modelos_relacionales/modelo_relacional_original.png) | ![Modelo relacional de PrediRuta](data/modelos_relacionales/modelo_relacional_prediruta.png) |

Los esquemas también están disponibles en formato [SQL](data/modelos_relacionales/modelo_relacional_prediruta.sql) y [DBML](data/modelos_relacionales/modelo_relacional_prediruta.txt).

## Obtención de los datos

### Siniestros viales

Los datos provienen del conjunto oficial [Siniestralidad BD](https://datos.movilidadbogota.gov.co/maps/ea243e7de8e846c8bd27e47c08771d66/about), publicado por la Secretaría Distrital de Movilidad de Bogotá. La información original incluye accidentes, vías, vehículos, actores viales, lesionados, fallecidos y causas.

Durante la limpieza se validaron las fechas, coordenadas y relaciones entre las tablas. También se conservaron únicamente los accidentes ubicados dentro del perímetro urbano de Bogotá y se retiraron datos sensibles o repetidos.

### Clima

El clima se obtuvo mediante [Open-Meteo](https://open-meteo.com/) a partir de dos fuentes:

- Antes de 2017 se utilizó **ERA5**, con una resolución aproximada de 25–28 km.
- Desde 2017 se utilizó **ECMWF IFS**, con una resolución aproximada de 9 km.

Para los datasets por accidente, el clima se relacionó con cada evento según su ubicación y hora:

- Cada accidente se asignó al punto meteorológico más cercano.
- La hora del accidente se aproximó a la observación horaria más cercana.
- Los accidentes que comparten punto y hora usan el mismo `CLIMA_ID`, evitando duplicar datos.

La tabla final incluye temperatura, humedad, sensación térmica, precipitación, lluvia, nubosidad, presión, velocidad y dirección del viento.

## Construcción del dataset de ocurrencia

`DATASET_OCURRENCIA.csv` se construye a partir de patrones históricos recurrentes, no mediante pares de casos y controles ni desplazando la fecha de los accidentes. El procedimiento es el siguiente:

1. Los accidentes se proyectan en `EPSG:3116` y se consolidan por celda espacial de 500 metros y hora. Si varios accidentes coinciden en una misma celda y hora, se representan mediante una sola observación positiva.
2. Las observaciones positivas se agrupan geográficamente en 150 zonas mediante `MiniBatchKMeans`.
3. Los casos se resumen por `ZONA_CIUDAD`, `MES`, `DIA_SEMANA` y `HORA`. Una combinación recibe `OCURRIO_ACCIDENTE = 1` si aparece al menos una vez en el histórico.
4. Se genera la cuadrícula completa de `150 × 12 × 7 × 24 = 302.400` combinaciones. Las combinaciones que no aparecen entre los accidentes históricos reciben `OCURRIO_ACCIDENTE = 0`.
5. A todas las combinaciones, tanto las etiquetadas con `1` como las etiquetadas con `0`, se les asigna una climatología para el mismo patrón de zona, mes, día de la semana y hora.

La climatología se calcula por nodo meteorológico y patrón temporal. Los resultados de ERA5 y ECMWF IFS se combinan ponderándolos por su cantidad de observaciones horarias; la dirección del viento se promedia de forma circular. Finalmente, cada zona recibe los valores del nodo meteorológico más cercano a su centroide.

> **Interpretación de los ceros:** `OCURRIO_ACCIDENTE = 0` significa que no se encontró un accidente en esa combinación recurrente durante el periodo histórico disponible. No representa la observación de una celda sin accidente en una fecha concreta. Por esta razón, el objetivo describe recurrencia histórica y no una probabilidad calibrada para una fecha futura específica.

Las variables finales de este dataset son:

- Espacio y tiempo: `MES`, `DIA_SEMANA`, `HORA`, `ZONA_CIUDAD`, `LATITUD_CENTROIDE` y `LONGITUD_CENTROIDE`.
- Clima: `TEMPERATURA_2M`, `HUMEDAD_RELATIVA_2M`, `SENSACION_TERMICA`, `PRECIPITACION`, `LLUVIA`, `NUBOSIDAD`, `PRESION_SUPERFICIE`, `VELOCIDAD_VIENTO_10M` y `DIRECCION_VIENTO_10M`.
- Variable objetivo: `OCURRIO_ACCIDENTE`.

## Flujo general

```text
Datos originales → limpieza y validación → tablas relacionales → datasets de modelado → modelos predictivos
```

El notebook `data/construccion_dataset.ipynb` genera:

- `DATASET_OCURRENCIA.csv`: cuadrícula completa de patrones recurrentes zona-mes-día-hora, con la etiqueta de ocurrencia histórica y la climatología correspondiente.
- `DATASET_EVENTOS.csv`: accidentes ocurridos para modelar `CLASE_ACCIDENTE` y `OBJETIVO_GRAVE`, con el clima observado asociado a cada evento.
- `TABLA_COMPLETA_ACCIDENTES.csv`: una fila por accidente con la información consolidada de las seis tablas, destinada al análisis histórico y exploratorio.
- `DICCIONARIO_CATEGORIAS.csv`: referencia reproducible de las variables categóricas codificadas.

Los productos se guardan en `data/data_procesada/modelado/`. Para el modelo de ocurrencia se comparan las mismas observaciones bajo dos configuraciones: variables espacio-temporales y variables espacio-temporales más clima.
