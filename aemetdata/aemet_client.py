"""Cliente principal para AEMET OpenData."""
import httpx

class AemetClient:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def download_data(self, endpoint):
        """Descarga datos de un endpoint de AEMET OpenData."""
        # Esta es una implementación mínima de ejemplo.
        # En la versión real, deberías gestionar la autenticación y la descarga real.
        url = f"https://opendata.aemet.es/opendata/api/{endpoint}"
        headers = {"accept": "application/json"}
        if self.api_key:
            headers["api_key"] = self.api_key
        resp = httpx.get(url, headers=headers)
        resp.raise_for_status()
        return resp.text
