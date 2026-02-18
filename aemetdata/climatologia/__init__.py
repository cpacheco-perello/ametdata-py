
"""
Módulo de climatología de AEMET.

Descarga datos climatológicos mensuales, diarios y valores normales y extremos

"""

from __future__ import annotations
from typing import Iterable
import re
import json
from datetime import datetime, timedelta
from ..utils.suport_functions import (
    fetch_con_reintentos_endpoint_aemet,
    fetch_json_url,
    AemetError,
    get_relativedelta,
)



async def datos_mensuales(
    idema: str,
    anio_inicio: int,
    anio_fin: int,
    api_keys: Iterable[str],
) -> dict:
    """Descarga los datos climatológicos mensuales por estación y rango de años.

    Args:
        idema: Identificador de estación (IDEMA).
        anio_inicio: Año inicial (incluido).
        anio_fin: Año final (incluido).
        api_keys: Iterable con las claves API de AEMET.
    """


    if isinstance(idema, str):
        idemas = [idema]
    elif isinstance(idema, (list, tuple)):
        idemas = list(idema)
    else:
        raise ValueError("El parámetro 'idema' debe ser str o iterable de str.")

    if not idemas:
        raise ValueError("El parámetro 'idema' es obligatorio.")

    if not isinstance(anio_inicio, int) or not isinstance(anio_fin, int):
        raise ValueError("'anio_inicio' y 'anio_fin' deben ser enteros.")

    if anio_inicio > anio_fin:
        raise ValueError("'anio_inicio' no puede ser mayor que 'anio_fin'.")


    api_keys_list = list(api_keys)
    if not api_keys_list:
        raise ValueError("Se requiere al menos una API key en 'api_keys'.")

    all_results = []
    for idema_item in idemas:
        anio_ini = anio_inicio
        while anio_ini <= anio_fin:
            anio_fin_intervalo = min(anio_ini + 2, anio_fin)
            endpoint_template = (
                "https://opendata.aemet.es/opendata/api/valores/climatologicos/"
                f"mensualesanuales/datos/anioini/{anio_ini}/aniofin/{anio_fin_intervalo}/"
                f"estacion/{idema_item}?api_key={{apiKey}}"
            )
            print(
                f"🔍 Solicitando climatología mensual para estación {idema_item} "
                f"entre {anio_ini} y {anio_fin_intervalo}"
            )
            response = await fetch_con_reintentos_endpoint_aemet(
                endpoint_template,
                tipo=f"climatologia_mensual_{idema_item}_{anio_ini}_{anio_fin_intervalo}",
                api_keys=api_keys_list,
            )
            if response.get("estado") != 200:
                raise AemetError(
                    f"Error en AEMET: {response.get('descripcion', 'Error desconocido')} "
                    f"(estado: {response.get('estado')})"
                )
            datos_url = response.get("datos")
            if not datos_url:
                raise AemetError("No se encontró URL de descarga en la respuesta de AEMET")
            print(f"✨ Descargando datos de climatología mensual desde URL de AEMET: {datos_url}")
            datos = await fetch_json_url(datos_url)
            print(f"✅ Datos de climatología mensual descargados exitosamente para estación {idema_item}")
            # Si es lista, concatenar
            if isinstance(datos, list):
                all_results.extend(datos)
            elif isinstance(datos, dict):
                all_results.append(datos)
            else:
                try:
                    data = json.loads(datos)
                    if isinstance(data, list):
                        all_results.extend(data)
                    elif isinstance(data, dict):
                        all_results.append(data)
                    else:
                        all_results.append({'contenido': str(datos)})
                except Exception:
                    all_results.append({'contenido': str(datos)})
            anio_ini = anio_fin_intervalo + 1
    return all_results


async def datos_diarios(
    idema: str,
    fecha_inicio: str,
    fecha_fin: str,
    api_keys: Iterable[str],
) -> dict:
    """Descarga los datos climatológicos diarios por estación y rango de fechas.

    Args:
        idema: Identificador de estación (IDEMA).
        fecha_inicio: Fecha inicial en formato 'AAAA-MM-DDTHH:MM:SSUTC' (ejemplo: '2022-01-01T00:00:00UTC').
        fecha_fin: Fecha final en formato 'AAAA-MM-DDTHH:MM:SSUTC' (ejemplo: '2022-01-31T23:59:59UTC').
        api_keys: Iterable con las claves API de AEMET."""
    
    if isinstance(idema, str):
        idemas = [idema]
    elif isinstance(idema, (list, tuple)):
        idemas = list(idema)
    else:
        raise ValueError("El parámetro 'idema' debe ser str o iterable de str.")

    if not idemas:
        raise ValueError("El parámetro 'idema' es obligatorio.")


    relativedelta = get_relativedelta()
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
            siguiente = actual + relativedelta(months=+5, days=+29)
            if siguiente > dt_fin:
                siguiente = dt_fin
            intervalos.append((actual, siguiente))
            actual = siguiente + timedelta(days=1)
        return intervalos

    intervalos = generar_intervalos(dt_inicio, dt_fin)

    api_keys_list = list(api_keys)
    if not api_keys_list:
        raise ValueError("Se requiere al menos una API key en 'api_keys'.")

    all_results = []
    for idema_item in idemas:
        for intervalo_inicio, intervalo_fin in intervalos:
            fecha_ini_str = intervalo_inicio.strftime('%Y-%m-%dT00:00:00UTC')
            fecha_fin_str = intervalo_fin.strftime('%Y-%m-%dT23:59:59UTC')
            endpoint_template = (
                "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/"
                f"fechaini/{fecha_ini_str}/fechafin/{fecha_fin_str}/estacion/{idema_item}?api_key={{apiKey}}"
            )
            print(
                f"🔍 Solicitando climatología diaria para estación {idema_item} "
                f"entre {fecha_ini_str} y {fecha_fin_str}"
            )
            response = await fetch_con_reintentos_endpoint_aemet(
                endpoint_template,
                tipo=f"climatologia_diaria_{idema_item}_{fecha_ini_str}_{fecha_fin_str}",
                api_keys=api_keys_list,
            )
            if response.get("estado") != 200:
                raise AemetError(
                    f"Error en AEMET: {response.get('descripcion', 'Error desconocido')} "
                    f"(estado: {response.get('estado')})"
                )
            datos_url = response.get("datos")
            if not datos_url:
                raise AemetError("No se encontró URL de descarga en la respuesta de AEMET")
            print(f"✨ Descargando datos de climatología diaria desde URL de AEMET: {datos_url}")
            datos = await fetch_json_url(datos_url)
            print(f"✅ Datos de climatología diaria descargados exitosamente para estación {idema_item}")
            # Si es lista, concatenar
            if isinstance(datos, list):
                all_results.extend(datos)
            elif isinstance(datos, dict):
                all_results.append(datos)
            else:
                try:
                    data = json.loads(datos)
                    if isinstance(data, list):
                        all_results.extend(data)
                    elif isinstance(data, dict):
                        all_results.append(data)
                    else:
                        all_results.append({'contenido': str(datos)})
                except Exception:
                    all_results.append({'contenido': str(datos)})
    return all_results



async def datos_extremos(
    idema: str,
    api_keys: Iterable[str],
    parametro: str | Iterable[str] = None,
) -> dict:
    """Descarga los valores extremos climatológicos por estación y parámetros.

    Args:
        idema: Identificador de estación (IDEMA).
        api_keys: Iterable con las claves API de AEMET.
        parametro: Parámetro o lista de parámetros (por defecto ["P", "T", "V"]).
    """
    if parametro is None:
        parametros = ["P", "T", "V"]
    elif isinstance(parametro, str):
        parametros = [parametro]
    elif isinstance(parametro, (list, tuple)):
        parametros = list(parametro)
    else:
        raise ValueError("El parámetro 'parametro' debe ser str o iterable de str.")
    if isinstance(idema, str):
        idemas = [idema]
    elif isinstance(idema, (list, tuple)):
        idemas = list(idema)
    else:
        raise ValueError("El parámetro 'idema' debe ser str o iterable de str.")

    if not idemas:
        raise ValueError("El parámetro 'idema' es obligatorio.")

    api_keys_list = list(api_keys)
    if not api_keys_list:
        raise ValueError("Se requiere al menos una API key en 'api_keys'.")

    all_results = []
    for idema_item in idemas:
        for parametro in parametros:
            endpoint_template = (
                "https://opendata.aemet.es/opendata/api/valores/climatologicos/valoresextremos/"
                f"parametro/{parametro}/estacion/{idema_item}?api_key={{apiKey}}"
            )
            print(f"🔍 Solicitando valores extremos para estación {idema_item}, parámetro {parametro}")
            response = await fetch_con_reintentos_endpoint_aemet(
                endpoint_template,
                tipo=f"climatologia_extremos_{idema_item}_{parametro}",
                api_keys=api_keys_list,
            )
            if response.get("estado") != 200:
                raise AemetError(
                    f"Error en AEMET: {response.get('descripcion', 'Error desconocido')} "
                    f"(estado: {response.get('estado')})"
                )
            datos_url = response.get("datos")
            if not datos_url:
                raise AemetError("No se encontró URL de descarga en la respuesta de AEMET")
            print(f"✨ Descargando valores extremos desde URL de AEMET: {datos_url}")
            datos = await fetch_json_url(datos_url)
            print(f"✅ Valores extremos descargados exitosamente para estación {idema_item}, parámetro {parametro}")
            if isinstance(datos, list):
                all_results.extend(datos)
            elif isinstance(datos, dict):
                all_results.append(datos)
            else:
                try:
                    data = json.loads(datos)
                    if isinstance(data, list):
                        all_results.extend(data)
                    elif isinstance(data, dict):
                        all_results.append(data)
                    else:
                        all_results.append({'contenido': str(datos)})
                except Exception:
                    all_results.append({'contenido': str(datos)})
    return all_results


async def datos_normales(
    idema: str,
    api_keys: Iterable[str],
) -> dict:
    """Descarga los valores normales climatológicos por estación.

    Args:
        idema: Identificador de estación (IDEMA).
        api_keys: Iterable con las claves API de AEMET.
    """
    if isinstance(idema, str):
        idemas = [idema]
    elif isinstance(idema, (list, tuple)):
        idemas = list(idema)
    else:
        raise ValueError("El parámetro 'idema' debe ser str o iterable de str.")

    if not idemas:
        raise ValueError("El parámetro 'idema' es obligatorio.")

    api_keys_list = list(api_keys)
    if not api_keys_list:
        raise ValueError("Se requiere al menos una API key en 'api_keys'.")

    all_results = []
    for idema_item in idemas:
        endpoint_template = (
            "https://opendata.aemet.es/opendata/api/valores/climatologicos/normales/"
            f"estacion/{idema_item}?api_key={{apiKey}}"
        )
        print(f"🔍 Solicitando valores normales para estación {idema_item}")
        response = await fetch_con_reintentos_endpoint_aemet(
            endpoint_template,
            tipo=f"climatologia_normales_{idema_item}",
            api_keys=api_keys_list,
        )
        if response.get("estado") != 200:
            raise AemetError(
                f"Error en AEMET: {response.get('descripcion', 'Error desconocido')} "
                f"(estado: {response.get('estado')})"
            )
        datos_url = response.get("datos")
        if not datos_url:
            raise AemetError("No se encontró URL de descarga en la respuesta de AEMET")
        print(f"✨ Descargando valores normales desde URL de AEMET: {datos_url}")
        datos = await fetch_json_url(datos_url)
        print(f"✅ Valores normales descargados exitosamente para estación {idema_item}")
        if isinstance(datos, list):
            all_results.extend(datos)
        elif isinstance(datos, dict):
            all_results.append(datos)
        else:
            try:
                data = json.loads(datos)
                if isinstance(data, list):
                    all_results.extend(data)
                elif isinstance(data, dict):
                    all_results.append(data)
                else:
                    all_results.append({'contenido': str(datos)})
            except Exception:
                all_results.append({'contenido': str(datos)})
    return all_results
