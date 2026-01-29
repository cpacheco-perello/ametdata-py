# aemetdata

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

## Uso rápido

```python
from aemetdata import AemetClient

client = AemetClient()
# Ejemplo de endpoint: "valores/climatologicos/diarios/datos/fechaini/2024-01-01T00:00:00UTC/fechafin/2024-01-02T00:00:00UTC/todasestaciones"
endpoint = "valores/climatologicos/diarios/datos/fechaini/2024-01-01T00:00:00UTC/fechafin/2024-01-02T00:00:00UTC/todasestaciones"

data = client.download_data(endpoint)
print(data[:500])
```

## CLI

```bash
aemetdata download \
  --endpoint "valores/climatologicos/diarios/datos/fechaini/2024-01-01T00:00:00UTC/fechafin/2024-01-02T00:00:00UTC/todasestaciones" \
  --output datos.json
```

## Publicación en PyPI

1. Actualiza `version` en pyproject.toml.
2. Construye el paquete:

```bash
python -m build
```

3. Sube a PyPI:

```bash
python -m twine upload dist/*
```

## Publicación en GitHub

1. Inicializa el repo:

```bash
git init
```

2. Añade archivos y commit:

```bash
git add .
git commit -m "Initial commit"
```

3. Crea el repo en GitHub y conecta el remoto:

```bash
git remote add origin https://github.com/tu-usuario/aemetdata.git
git branch -M main
git push -u origin main
```

## Licencia

MIT. Ver [LICENSE](LICENSE).
