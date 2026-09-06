# PrediRuta

PrediRuta es un proyecto aplicado de analítica de datos orientado al estudio de la siniestralidad vial en Bogotá. Integra datos de accidentes, actores, vehículos, vías, causas y clima para estudiar tres problemas predictivos: ocurrencia de accidentes, estado del actor involucrado y clase de accidente.

El enfoque actual prioriza dos componentes para el MVP:

1. estimar la ocurrencia histórica de accidentes por zona y patrón temporal;
2. estimar, condicionado a que ocurra un accidente, las probabilidades de que un actor resulte `HERIDO`, `ILESO` o `MUERTO`.

La predicción de la clase del accidente se conserva como experimento, pero no se recomienda para uso operativo debido a su desempeño limitado.

## Estructura del proyecto

```text
Prediruta/
├── data/
│   ├── data/                         # Fuentes originales
│   ├── data_procesada/modelado/     # Tablas y datasets finales
│   ├── modelos_relacionales/        # Diagramas y esquemas SQL/DBML
│   ├── limpieza_estructuracion_bd.ipynb
│   ├── construccion_dataset.ipynb
│   └── carga_csv_supabase.ipynb
├── modelo/
│   ├── modelo_ocurrencia_accidente.ipynb
│   ├── modelo_estado_victima.ipynb
│   ├── modelo_clase_accidente.ipynb
│   └── modelos_produccion/          # Modelo de estado y metadatos
├── notebooks/                            # Prototipos de consulta y visualización
├── frontend/                             # Espacio reservado para la interfaz
└── entregas/                             # Documentos de las entregas académicas
```

## Fuentes y modelo relacional

Los datos de siniestros provienen del conjunto oficial [Siniestralidad BD](https://datos.movilidadbogota.gov.co/maps/ea243e7de8e846c8bd27e47c08771d66/about), publicado por la Secretaría Distrital de Movilidad de Bogotá. Durante la limpieza se validan fechas, coordenadas y relaciones entre tablas; se conservan los accidentes dentro del perímetro urbano y se retiran datos sensibles o redundantes.

El modelo depurado contiene:

- `ACCIDENTE`: fecha, coordenadas, clase y objetivo de gravedad.
- `ACTOR_VIAL`: personas involucradas de forma anonimizada.
- `VEHICULO`: vehículos relacionados con los actores.
- `VIA`: características y condiciones de la vía.
- `CAUSA`: causas registradas para el accidente.
- `CLIMA`: observaciones meteorológicas horarias.

`ACCIDENTE_ID`, `ACTOR_ID`, `VEHICULO_ID`, `CAUSA_ID` y `CLIMA_ID` permiten relacionar las tablas mediante identificadores enteros.

| Modelo original | Modelo depurado de PrediRuta |
|---|---|
| ![Modelo relacional original](data/modelos_relacionales/modelo_relacional_original.png) | ![Modelo relacional de PrediRuta](data/modelos_relacionales/modelo_relacional_prediruta.png) |

Los esquemas también están disponibles en formato [SQL](data/modelos_relacionales/modelo_relacional_prediruta.sql) y [DBML](data/modelos_relacionales/modelo_relacional_prediruta.txt).

## Integración del clima

Las variables meteorológicas se obtienen de [Open-Meteo](https://open-meteo.com/) mediante dos fuentes históricas:

- antes de 2017: ERA5, con resolución aproximada de 25–28 km;
- desde 2017: ECMWF IFS, con resolución aproximada de 9 km.

Cada accidente se relaciona con el nodo meteorológico más cercano y con la observación horaria correspondiente. La información disponible incluye temperatura, humedad, sensación térmica, precipitación, lluvia, nubosidad, presión y viento.

Para evitar redundancia entre variables altamente correlacionadas, los notebooks de estado y clase evalúan un subconjunto meteorológico. Se evita usar simultáneamente temperatura con sensación térmica y precipitación con lluvia. El aporte del clima se estudia comparando escenarios equivalentes con y sin estas variables.

## Construcción de los datasets

El notebook [`data/construccion_dataset.ipynb`](data/construccion_dataset.ipynb) integra y transforma las fuentes. Sus productos se guardan en `data/data_procesada/modelado/`.

| Archivo | Unidad de observación | Uso principal |
|---|---|---|
| `DATASET_OCURRENCIA.csv` | Zona, mes, día de la semana y hora | Modelo de ocurrencia |
| `DATASET_EVENTOS.csv` | Accidente | Análisis de eventos y objetivos por accidente |
| `TABLA_COMPLETA_MODELADO.csv` | Actor involucrado en un accidente | Modelos de estado y clase de accidente |
| `DICCIONARIO_CATEGORIAS.csv` | Categoría codificada | Interpretación reproducible de variables categóricas |

La tabla completa de modelado consolida en un solo archivo la información necesaria de accidente, actor, vehículo, vía, clase, clima y zona. De esta manera, los notebooks de estado y clase no necesitan cargar por separado `ACTOR_VIAL.csv`, `VEHICULO.csv` o `DATASET_OCURRENCIA.csv`.

### Dataset de ocurrencia

`DATASET_OCURRENCIA.csv` no genera negativos desplazando las fechas de los accidentes. El procedimiento actual es:

1. proyectar los accidentes en `EPSG:3116` y consolidarlos espacial y temporalmente;
2. construir 150 zonas geográficas mediante `MiniBatchKMeans`;
3. resumir los positivos por `ZONA_CIUDAD`, `MES`, `DIA_SEMANA` y `HORA`;
4. generar las `150 × 12 × 7 × 24 = 302.400` combinaciones posibles;
5. asignar `OCURRIO_ACCIDENTE = 0` a las combinaciones sin registros históricos;
6. incorporar la climatología correspondiente a cada zona y patrón temporal.

Un cero significa que no se encontró un accidente para esa combinación recurrente en el histórico disponible. No representa la observación de una zona sin accidente en una fecha futura concreta. La salida debe interpretarse como recurrencia histórica y no como una probabilidad temporal perfectamente calibrada.

## Modelos

### 1. Ocurrencia de accidentes

[`modelo/modelo_ocurrencia_accidente.ipynb`](modelo/modelo_ocurrencia_accidente.ipynb) compara regresión logística, Random Forest, XGBoost y MLP. Utiliza las 150 zonas y estudia configuraciones espacio-temporales con y sin variables meteorológicas. El notebook incluye tablas de métricas y una comparación gráfica final.

La carga local utiliza:

```python
pd.read_csv('../data/data_procesada/modelado/DATASET_OCURRENCIA.csv')
```

Las rutas de Kaggle se conservan comentadas como referencia.

### 2. Estado del actor

[`modelo/modelo_estado_victima.ipynb`](modelo/modelo_estado_victima.ipynb) estima las probabilidades de `HERIDO`, `ILESO` y `MUERTO`, condicionado a la ocurrencia de un accidente. Emplea las mismas 150 zonas del modelo de ocurrencia, pero trabaja solamente con eventos positivos y excluye `SIN INFORMACION` del objetivo.

El notebook compara:

- alcance completo y alcance operativo;
- escenarios con y sin clima;
- regresión logística, Random Forest, XGBoost y MLP.

La selección se realiza con `F1_macro`, `Balanced_Accuracy` y `Log_Loss`. La evaluación principal conserva el orden temporal: los años históricos se usan para entrenamiento, 2021–2023 para validación y 2024–2026 como prueba final no utilizada durante la selección. `ANIO` define los cortes, pero no entra como predictor.

Como análisis de sensibilidad también se ejecuta una partición aleatoria por accidente. Esta produce resultados más optimistas, por lo que la partición temporal se mantiene como referencia para estimar la generalización hacia periodos futuros.

El escenario operativo seleccionado no utiliza clima y se exporta en `modelo/modelos_produccion/` junto con sus centroides y metadatos. La salida puede presentarse como una distribución de probabilidades entre los tres estados; no debe interpretarse como certeza individual.

### 3. Clase de accidente

[`modelo/modelo_clase_accidente.ipynb`](modelo/modelo_clase_accidente.ipynb) clasifica los accidentes en `CHOQUE`, `ATROPELLO` y `OTROS`; esta última agrupa las categorías minoritarias restantes.

La tabla se reduce a una fila por `ACCIDENTE_ID` y excluye `SIN INFORMACION`. El diseño experimental replica la estructura del modelo de estado: mismos algoritmos, escenarios completo y operativo, comparación con y sin clima, partición temporal, backtesting y contraste con partición aleatoria.

Aunque el modelo supera la línea base, su desempeño temporal es limitado (`F1_macro` cercano a 0,37 y `Balanced_Accuracy` cercana a 0,39), especialmente para `OTROS` y `ATROPELLO`. Se documenta como resultado experimental, pero no se incorpora al flujo productivo del MVP.

## Diseño de evaluación

Para estado y clase se mantiene el siguiente criterio:

1. usar las zonas definidas por el modelo de ocurrencia;
2. retirar categorías sin información antes de dividir los datos;
3. comparar los escenarios sobre las mismas observaciones;
4. ajustar los hiperparámetros de cada alcance con clima y reutilizarlos sin clima para aislar su aporte;
5. seleccionar modelos exclusivamente con validación;
6. reajustar el ganador con los datos disponibles hasta 2023;
7. evaluar una sola vez sobre 2024–2026;
8. mantener `ANIO` fuera de los predictores.

La exactitud global no se utiliza como único criterio porque los objetivos son desbalanceados. `F1_macro` asigna la misma importancia a cada clase, mientras que `Balanced_Accuracy` resume el recall medio entre clases. Las métricas probabilísticas complementan el análisis cuando el uso esperado requiere reportar probabilidades.

## Orden recomendado de ejecución

Desde la raíz del proyecto:

1. `data/limpieza_estructuracion_bd.ipynb`;
2. `data/construccion_dataset.ipynb`;
3. `modelo/modelo_ocurrencia_accidente.ipynb`;
4. `modelo/modelo_estado_victima.ipynb`;
5. `modelo/modelo_clase_accidente.ipynb`, solo para reproducir el experimento de clase.

Los notebooks de la carpeta `modelo/` usan rutas relativas hacia `../data/data_procesada/modelado/`, por lo que deben ejecutarse manteniendo esa estructura de directorios.

## Artefactos disponibles

El modelo de estado seleccionado cuenta con los siguientes archivos de producción:

- `modelo_estado_actor_xgboost.joblib`: pipeline entrenado;
- `metadata_estado_actor.joblib`: clases, variables y configuración necesaria para inferencia;
- `centroides_zonas.csv`: centroides utilizados para asignar una ubicación a `ZONA_CIUDAD`.

Actualmente no se exporta un modelo productivo de clase de accidente.
