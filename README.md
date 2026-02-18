
# aemetdata

![PyPI](https://img.shields.io/pypi/v/python-aemet)
![PyPI - Downloads](https://img.shields.io/pypi/dm/python-aemet)

**Inspiración y recursos relacionados:**

Esta librería se inspira en [python-aemet](https://pypi.org/project/python-aemet/), una librería cliente de la API de datos de AEMET. Permite obtener y manejar la información de la API de datos abiertos de AEMET, con modelos de datos y métodos preparados para facilitar su uso. Además, permite descargar en archivos los mapas que genera y publica AEMET.

La información que recoge y utiliza esta librería es propiedad de la Agencia Estatal de Meteorología.

**Instalación de python-aemet:**

```bash
pip install python-aemet
```

**API Key:**

Obtén tu clave de API en la siguiente URL:
https://opendata.aemet.es/centrodedescargas/obtencionAPIKey

**Ejemplo de uso de python-aemet:**

```python
from aemet import Aemet
aemet_client = Aemet(api_key='your_api_key')
```

Instancia un objeto con la API key y tendrás acceso a todos los métodos.

Para más información, revisa la documentación oficial de cada librería.

**aemetdata** es un paquete Python que permite descargar y procesar datos meteorológicos de AEMET OpenData de forma sencilla y eficiente. Proporciona un cliente de alto nivel para acceder a los principales endpoints de la API, así como utilidades para automatizar la descarga, gestión y análisis de datos climáticos y de observación en España.


## Funcionalidades principales

El paquete aemetdata proporciona las siguientes funciones y módulos:

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



Consulta la documentación y los notebooks de ejemplo para ver casos de uso detallados.

Cliente Python para descargar datos de **AEMET OpenData** con un flujo simple de dos pasos (solicitud → URL de datos → descarga).

## Instalación

```bash
pip install aemetdata
```

## Configuración

Necesitas una API Key de AEMET OpenData. Puedes pasarla como argumento o definir la variable de entorno:

```bash
export AEMET_API_KEY="tu_api_key"
```

En Windows (PowerShell):

```powershell
setx AEMET_API_KEY "tu_api_key"
```


## Uso rápido (Python)
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

```python
from aemetdata import AemetClient

client = AemetClient()
# Ejemplo de endpoint: "valores/climatologicos/diarios/datos/fechaini/2024-01-01T00:00:00UTC/fechafin/2024-01-02T00:00:00UTC/todasestaciones"
endpoint = "valores/climatologicos/diarios/datos/fechaini/2024-01-01T00:00:00UTC/fechafin/2024-01-02T00:00:00UTC/todasestaciones"

data = client.download_data(endpoint)
print(data[:500])
```



## Licencia

MIT. Ver [LICENSE](LICENSE).
