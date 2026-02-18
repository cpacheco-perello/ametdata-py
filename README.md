
![PyPI](https://img.shields.io/pypi/v/aemetdata)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aemetdata)
![PyPI - Status](https://img.shields.io/pypi/status/aemetdata)
![GitHub issues](https://img.shields.io/github/issues/cpacheco-perello/aemetdata-py)
![GitHub last commit](https://img.shields.io/github/last-commit/cpacheco-perello/aemetdata-py)

# aemetdata

**aemetdata** es un paquete Python para descargar y procesar datos meteorológicos de AEMET OpenData de forma sencilla y eficiente.

La información que recoge y utiliza esta librería es propiedad de la Agencia Estatal de Meteorología.

## Instalación

```bash
pip install aemetdata
```

## Obtención de API Key

Necesitas una API Key de AEMET OpenData. Puedes obtenerla en:
[Obtener clave api AEMET](https://opendata.aemet.es/centrodedescargas/altaUsuario?)

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
  

  ```python
  from aemetdata import AemetClient

  client = AemetClient(api_key=API_KEY)
  endpoint = "valores/climatologicos/diarios/datos/fechaini/2024-01-01T00:00:00UTC/fechafin/2024-01-02T00:00:00UTC/todasestaciones"
  data = client.download_data(endpoint)
  print(data[:500])
  ```

- **aemetdata.avisos**: Funciones para descargar avisos meteorológicos oficiales:
  - `avisos_area_ultimo_eleaborado(codigo_area, api_key)`: Descarga el último aviso elaborado para un área específica.
    ```python
    from aemetdata.avisos import avisos_area_ultimo_eleaborado
    ruta = await avisos_area_ultimo_eleaborado("72", [API_KEY])
    print(f"Archivo guardado: {ruta}")
    ```
  - `avisos_por_fechas(fecha_ini, fecha_fin, api_key)`: Descarga todos los avisos entre dos fechas.
    ```python
    from aemetdata.avisos import avisos_por_fechas
    rutas = await avisos_por_fechas('2026-01-01', '2026-01-04', [API_KEY])
    print('Archivos guardados:')
    for ruta in rutas:
        print(ruta)
    ```


- **aemetdata.climatologia**: Funciones para obtener datos climatológicos:
  - `datos_mensuales(estaciones, año_ini, año_fin, api_key)`: Descarga datos mensuales de climatología para una o varias estaciones.
    ```python
    from aemetdata.climatologia import datos_mensuales
    resultado = await datos_mensuales(["3195","3427Y"], 2020, 2024, [API_KEY])
    import pandas as pd
    pd.DataFrame(resultado)
    ```
  - `datos_diarios(estaciones, fecha_ini, fecha_fin, api_key)`: Descarga datos diarios de climatología.
    ```python
    from aemetdata.climatologia import datos_diarios
    resultado = await datos_diarios(["3195","3427Y"], '2022-01-01', '2022-08-10', [API_KEY])
    import pandas as pd
    pd.DataFrame(resultado)
    ```
  - `datos_normales(estaciones, api_key)`: Obtiene valores climatológicos normales (periodo 1991-2020).
    ```python
    from aemetdata.climatologia import datos_normales
    resultado_normales = await datos_normales(["3195","3427Y"], [API_KEY])
    import pandas as pd
    pd.DataFrame(resultado_normales)
    ```
  - `datos_extremos(estaciones, api_key, parametro)`: Descarga valores extremos (precipitación, temperatura, viento).
    ```python
    from aemetdata.climatologia import datos_extremos
    resultado_extremos_T = await datos_extremos(["3195","3427Y"], [API_KEY], parametro="T")
    import pandas as pd
    pd.DataFrame(resultado_extremos_T)
    ```

- **aemetdata.imagenes**: Funciones para descargar imágenes meteorológicas (satélite, radar, etc.).

- **aemetdata.observaciones**: Funciones para obtener observaciones meteorológicas en tiempo real.





