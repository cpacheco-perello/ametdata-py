"""Módulo de avisos de AEMET."""


from __future__ import annotations

from typing import Iterable

import httpx
from datetime import datetime
import httpx
from ..utils.suport_functions import (
    fetch_con_reintentos_endpoint_aemet,
    descargar_archivo_tar_gz,
    AemetError,
)


# Códigos de área válidos para AEMET
AREA_CODES = {
    "esp": "España",
    "61": "Andalucía",
    "62": "Aragón",
    "63": "Asturias, Principado de",
    "64": "Ballears, Illes",
    "78": "Ceuta",
    "65": "Canarias",
    "66": "Cantabria",
    "67": "Castilla y León",
    "68": "Castilla - La Mancha",
    "69": "Cataluña",
    "77": "Comunitat Valenciana",
    "70": "Extremadura",
    "71": "Galicia",
    "72": "Madrid, Comunidad de",
    "79": "Melilla",
    "73": "Murcia, Región de",
    "74": "Navarra, Comunidad Foral de",
    "75": "País Vasco",
    "76": "Rioja, La",
}


async def avisos_area_ultimo_eleaborado(area: str, api_keys: Iterable[str]):
    
    """Descarga los avisos del último elaborado para un área específica.
    
    Args:
        area: Código del área. Códigos válidos:
              - 'esp': España (todo el país)
              - '61': Andalucía
              - '62': Aragón
              - '63': Asturias, Principado de
              - '64': Ballears, Illes
              - '78': Ceuta
              - '65': Canarias
              - '66': Cantabria
              - '67': Castilla y León
              - '68': Castilla - La Mancha
              - '69': Cataluña
              - '77': Comunitat Valenciana
              - '70': Extremadura
              - '71': Galicia
              - '72': Madrid, Comunidad de
              - '79': Melilla
              - '73': Murcia, Región de
              - '74': Navarra, Comunidad Foral de
              - '75': País Vasco
              - '76': Rioja, La
        api_keys: Iterable con las claves API de AEMET.
        
    Returns:
        dict: Datos extraídos del archivo tar.gz con los avisos CAP.
              Estructura: {nombre_archivo: contenido_xml_o_json}
        
    Raises:
        ValueError: Si el área no es válida o si no hay API keys.
        AemetError: Si hay error descargando los datos.
    """
    if not area:
        raise ValueError("El parámetro 'area' es obligatorio.")

    if area not in AREA_CODES:
        valid_areas = ", ".join(AREA_CODES.keys())
        raise ValueError(
            f"Código de área '{area}' no válido. "
            f"Códigos válidos: {valid_areas}"
        )

    api_keys_list = list(api_keys)
    if not api_keys_list:
        raise ValueError("Se requiere al menos una API key en 'api_keys'.")

    endpoint_template = (
        f"https://opendata.aemet.es/opendata/api/avisos_cap/ultimoelaborado/area/{area}"
        "?api_key={apiKey}"
    )

    # Paso 1: Obtener la URL del archivo tar.gz
    print(f"🔍 Solicitando avisos para área {area} ({AREA_CODES[area]})")
    response = await fetch_con_reintentos_endpoint_aemet(
        endpoint_template,
        tipo=f"avisos_area_{area}",
        api_keys=api_keys_list,
    )
    
    # Paso 2: Validar respuesta
    if not isinstance(response, dict):
        raise AemetError(f"Respuesta inesperada de AEMET: {response}")
    
    if response.get("estado") != 200:
        raise AemetError(
            f"Error en AEMET: {response.get('descripcion', 'Error desconocido')} "
            f"(estado: {response.get('estado')})"
        )
    
    datos_url = response.get("datos")
    if not datos_url:
        raise AemetError("No se encontró URL de descarga en la respuesta de AEMET")
    
    # Paso 3: Descargar archivo tar.gz y guardarlo en disco
    print(f"✨ Descargando archivo tar.gz de avisos CAP desde URL de AEMET")
    async with httpx.AsyncClient() as client:
        resp = await client.get(datos_url, timeout=30)
        resp.raise_for_status()
        filename = f"avisos_area_{area}_{datetime.now().strftime('%Y%m%d%H%M%S')}.tar.gz"
        with open(filename, "wb") as f:
            f.write(resp.content)
        return filename


async def avisos_por_fechas(
    fecha_inicio: str,
    fecha_fin: str,
    api_keys: Iterable[str],
) -> dict:
    """Descarga los avisos CAP en un rango de fechas específico.
    
    Args:
        fecha_inicio: Fecha de inicio en formato ISO (ej: 2026-01-01 o 2026-01-01T00:00:00UTC).
        fecha_fin: Fecha de fin en formato ISO (ej: 2026-01-31 o 2026-01-31T23:59:59UTC).
        api_keys: Iterable con las claves API de AEMET.
        
    Returns:
        dict: Datos extraídos con los avisos CAP en el rango de fechas.
              Estructura: {nombre_archivo: contenido_xml_o_json}
        
    Raises:
        ValueError: Si las fechas no son válidas o si no hay API keys.
        AemetError: Si hay error descargando los datos.
        
    Example:
        >>> avisos = await avisos_por_fechas(
        ...     "2026-01-01",
        ...     "2026-01-31",
        ...     ["tu_api_key"]
        ... )
    """
    from datetime import datetime
    
    api_keys_list = list(api_keys)
    if not api_keys_list:
        raise ValueError("Se requiere al menos una API key en 'api_keys'.")
    
    # Validar formato de fechas básico
    if not fecha_inicio or not fecha_fin:
        raise ValueError("Los parámetros 'fecha_inicio' y 'fecha_fin' son obligatorios.")

    import re
    formato_fecha_completa = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}UTC$"
    formato_fecha_simple = r"^\d{4}-\d{2}-\d{2}$"

    def completar_fecha(fecha: str, inicio: bool) -> str:
        if re.match(formato_fecha_completa, fecha):
            return fecha
        elif re.match(formato_fecha_simple, fecha):
            return f"{fecha}T00:00:00UTC" if inicio else f"{fecha}T23:59:59UTC"
        else:
            raise ValueError(
                f"La fecha '{fecha}' debe estar en formato 'AAAA-MM-DD' o 'AAAA-MM-DDTHH:MM:SSUTC'."
            )

    fecha_inicio = completar_fecha(fecha_inicio, True)
    fecha_fin = completar_fecha(fecha_fin, False)

    from datetime import datetime, timedelta
    def parse_fecha(fecha):
        if 'T' in fecha:
            return datetime.strptime(fecha, '%Y-%m-%dT%H:%M:%SUTC')
        return datetime.strptime(fecha, '%Y-%m-%d')

    dt_inicio = parse_fecha(fecha_inicio)
    dt_fin = parse_fecha(fecha_fin)

    def generar_intervalos(dt_inicio, dt_fin):
        intervalos = []
        actual = dt_inicio
        while actual <= dt_fin:
            siguiente = actual + timedelta(days=1)
            if siguiente > dt_fin:
                siguiente = dt_fin
            intervalos.append((actual, siguiente))
            actual = siguiente + timedelta(days=1)
        return intervalos

    intervalos = generar_intervalos(dt_inicio, dt_fin)
    
    archivos = []
    rutas = []
    for intervalo_inicio, intervalo_fin in intervalos:
        fecha_ini_str = intervalo_inicio.strftime('%Y-%m-%dT00:00:00UTC')
        fecha_fin_str = intervalo_fin.strftime('%Y-%m-%dT23:59:59UTC')
        endpoint_template = (
            f"https://opendata.aemet.es/opendata/api/avisos_cap/archivo/"
            f"fechaini/{fecha_ini_str}/fechafin/{fecha_fin_str}"
            "?api_key={apiKey}"
        )
        print(f"🔍 Solicitando avisos CAP desde {fecha_ini_str} a {fecha_fin_str}")
        response = await fetch_con_reintentos_endpoint_aemet(
            endpoint_template,
            tipo=f"avisos_fechas_{fecha_ini_str}_{fecha_fin_str}",
            api_keys=api_keys_list,
        )
        if not isinstance(response, dict):
            raise AemetError(f"Respuesta inesperada de AEMET: {response}")
        if response.get("estado") != 200:
            raise AemetError(
                f"Error en AEMET: {response.get('descripcion', 'Error desconocido')} "
                f"(estado: {response.get('estado')})"
            )
        datos_url = response.get("datos")
        if not datos_url:
            raise AemetError("No se encontró URL de descarga en la respuesta de AEMET")
        print(f"✨ Descargando archivo tar.gz de avisos CAP desde URL de AEMET")
        async with httpx.AsyncClient() as client:
            resp = await client.get(datos_url, timeout=30)
            resp.raise_for_status()
            filename = f"avisos_{fecha_ini_str[:10]}_{fecha_fin_str[:10]}.tar.gz"
            with open(filename, "wb") as f:
                f.write(resp.content)
            rutas.append(filename)
    return rutas




