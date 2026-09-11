# PrediRuta

Aplicación web que compara las condiciones de un recorrido futuro dentro de
Bogotá con patrones históricos de ocurrencia de siniestros. El resultado integra
la ruta, el tiempo estimado, el pronóstico de Google Weather y una estimación
condicional del estado del actor en los sectores con mayor similitud histórica.

## Alcance

- La ruta se divide cuando cruza el límite entre las 150 zonas usadas durante
  el entrenamiento.
- PrediRuta comprueba todos los puntos de la geometría devuelta por Google. Si
  el recorrido sale del área urbana cubierta —por ejemplo, por Cota— se detiene
  antes de consultar clima o ejecutar los modelos.
- Google Routes API calcula la geometría inicial y vuelve a calcular una
  duración para cada tramo delimitado por las zonas.
- Google Weather API consulta el pronóstico horario para el punto medio espacial
  y temporal de cada tramo.
- El modelo de ocurrencia combina zona, mes, día, hora, temperatura,
  precipitación, nubosidad, presión y viento. Genera un índice relativo entre 0
  y 1 que permite ordenar patrones, pero no representa una probabilidad
  individual de accidente.
- El umbral de ocurrencia (`0,309018...`) se lee desde los metadatos exportados
  por el entrenamiento. Verde indica que el patrón no fue detectado; naranja,
  que superó el umbral; y rojo identifica hasta los tres scores detectados más
  altos dentro del recorrido.
- En esos sectores prioritarios, el modelo de estado muestra una distribución
  condicional entre HERIDO, ILESO y MUERTO.
- La lectura principal ordena los cinco scores más altos y usa Geocoding API
  para describir el inicio y el final de cada sector. El detalle completo del
  recorrido permanece disponible debajo.
- La aplicación no recomienda rutas ni emite instrucciones de conducción.

## Datos adicionales y privacidad

El modelo operativo de estado necesita edad, género, clase de vehículo y
servicio del vehículo. El usuario debe aceptar expresamente su uso antes de
ejecutar la consulta. El backend procesa estos valores en memoria, no los
escribe en archivos o bases de datos y no los incluye en la respuesta.

El frontend conserva el resultado en la sesión activa de Streamlit para evitar
perder el mapa en cada interacción. Al cerrar la sesión no existe persistencia
implementada por PrediRuta.

## Flujo técnico

1. El frontend valida campos, consentimiento y horizonte de siete días.
2. La API repite esas validaciones para impedir que se omitan desde otro cliente.
3. Google Routes construye el recorrido con tráfico.
4. La polilínea se densifica cada 100 metros y se asigna al centroide más cercano.
5. Cada cambio de zona crea un tramo nuevo.
6. Los límites de zona se envían a Google como puntos intermedios para obtener
   una duración por tramo.
7. Google Weather consulta el pronóstico horario de cada tramo. Como Google
   informa presión a nivel del mar y el modelo usa presión superficial, la API
   realiza la conversión con la elevación del nodo climático de entrenamiento.
8. Se ejecuta el modelo de ocurrencia con las variables meteorológicas y, en el
   nivel alto, el modelo complementario de estado.

## Ejecución local

Desde esta carpeta:

```bash
cp .env.example .env
# Configura GOOGLE_APIKEY en .env

docker build -f Dockerfile.api -t prediruta-api .
docker run -d -p 8000:8000 --env-file .env --name api_local prediruta-api

docker build -f Dockerfile.front -t prediruta-front .
docker run -d -p 8501:8501 \
  --env-file .env \
  -e API_URL=http://host.docker.internal:8000/predict \
  --name front_local prediruta-front
```

- Aplicación: http://localhost:8501
- Documentación de la API: http://localhost:8000/docs

Para el flujo completo debes habilitar **Routes API**, **Weather API**,
**Geocoding API**, **Places API (New)** y **Maps JavaScript API**. Routes,
Weather y Geocoding se consumen desde el backend; Places se usa en el
autocompletado; Maps JavaScript y su biblioteca Routes dibujan la vista previa
en el navegador.

En local puedes reutilizar `GOOGLE_APIKEY` para los servicios de Google. En
producción es preferible separar las credenciales: una clave privada para el
backend, otra privada para Places y una clave pública del mapa restringida por
dominio.

## Estructura

```text
app/
├── api/
│   ├── api.py          # Orquestación y contrato HTTP
│   ├── predictors.py   # Carga e inferencia de modelos
│   ├── schemas.py      # Validación de entradas
│   ├── services.py     # Google Routes, Weather, Geocoding y zonas
│   └── utils.py        # Operaciones sobre polilíneas
├── front/
│   ├── front_streamlit.py       # Flujo y presentación
│   ├── google_maps_components.py # Places y mapas embebidos
│   └── project_info.py           # Vista informativa del proyecto y sus resultados
├── modelo/
├── Dockerfile.api
├── Dockerfile.front
├── requirements.api.txt
├── requirements.front.txt
└── requirements.txt
```

## Variables de entorno

| Variable | Servicio | Uso |
| --- | --- | --- |
| `GOOGLE_APIKEY` | API | Autenticación en Google Routes y Weather |
| `GOOGLE_PLACES_APIKEY` | Frontend | Autocompletado de Places API (New) desde el servidor |
| `GOOGLE_MAPS_BROWSER_KEY` | Navegador | Maps JavaScript y vista previa con Directions |
| `API_URL` | Frontend | URL completa del endpoint `/predict` |
| `APP_ENV` | Frontend | Permite reutilizar `GOOGLE_APIKEY` solo durante la prueba local |
| `PORT` | Ambos | Puerto asignado por la plataforma de despliegue |

Nunca copies el archivo `.env` dentro de una imagen ni lo publiques en el
repositorio. `.dockerignore` lo excluye del contexto enviado a Docker.
