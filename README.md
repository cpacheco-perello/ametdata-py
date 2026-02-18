![PyPI](https://img.shields.io/pypi/v/aemetdata)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aemetdata)

# aemetdata

**aemetdata** es un paquete Python para descargar y procesar datos meteorológicos de AEMET OpenData de forma sencilla y eficiente.

La información que recoge y utiliza esta librería es propiedad de la Agencia Estatal de Meteorología.

## Instalación

```bash
pip install aemetdata
```

## Obtención de API Key

Necesitas una API Key de AEMET OpenData. Puedes obtenerla en:
[https://opendata.aemet.es/centrodedescargas/altaUsuario?](https://opendata.aemet.es/centrodedescargas/altaUsuario?)

Puedes pasarla como argumento o definir la variable de entorno:

```bash
export AEMET_API_KEY="tu_api_key"
```

En Windows (PowerShell):

```powershell
setx AEMET_API_KEY "tu_api_key"
```

## Cliente y funciones principales

- **AemetClient**: Clase principal para interactuar con la API de AEMET OpenData. Permite descargar datos de cualquier endpoint autorizado.
- **aemetdata.avisos**: Funciones para descargar avisos meteorológicos oficiales:
  - `avisos_area_ultimo_eleaborado(codigo_area, api_key)`: Descarga el último aviso elaborado para un área específica.
  - `avisos_por_fechas(fecha_ini, fecha_fin, api_key)`: Descarga todos los avisos entre dos fechas.

- **aemetdata.climatologia**: Funciones para obtener datos climatológicos:
  - `datos_mensuales(estaciones, año_ini, año_fin, api_key)`: Descarga datos mensuales de climatología para una o varias estaciones.
  - `datos_diarios(estaciones, fecha_ini, fecha_fin, api_key)`: Descarga datos diarios de climatología.
  - `datos_normales(estaciones, api_key)`: Obtiene valores climatológicos normales (periodo 1991-2020).
  - `datos_extremos(estaciones, api_key, parametro)`: Descarga valores extremos (precipitación, temperatura, viento).

- **aemetdata.imagenes**: Funciones para descargar imágenes meteorológicas (satélite, radar, etc.).

- **aemetdata.observaciones**: Funciones para obtener observaciones meteorológicas en tiempo real.

- **aemetdata.utils**: Funciones de soporte para manejo de fechas, descargas y descompresión de archivos.



data = client.download_data(endpoint)

## Ejemplo de uso en Python

```python
from aemetdata import AemetClient

client = AemetClient(api_key="TU_API_KEY")
# Ejemplo de endpoint:
endpoint = "valores/climatologicos/diarios/datos/fechaini/2024-01-01T00:00:00UTC/fechafin/2024-01-02T00:00:00UTC/todasestaciones"
data = client.download_data(endpoint)
print(data[:500])
```

## Uso desde la terminal (CLI)

Puedes consultar los alias de endpoints disponibles con:

```bash
python -m aemetdata.cli --list
```

Ejemplo de descarga usando un alias:

```bash
python -m aemetdata.cli --alias diarios --param fechaini=2024-01-01 fechafin=2024-01-02 --api-key TU_API_KEY --output datos.json
```

También puedes usar el endpoint completo como antes:

```bash
python -m aemetdata.cli --endpoint "valores/climatologicos/diarios/datos/fechaini/2024-01-01T00:00:00UTC/fechafin/2024-01-02T00:00:00UTC/todasestaciones" --api-key TU_API_KEY --output datos.json
```



