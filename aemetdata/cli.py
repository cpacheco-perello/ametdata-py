"""Interfaz CLI para aemetdata."""


def parse_params(params: list[str]) -> dict[str, str]:
    """Parsea parámetros en formato clave=valor.
    
    Args:
        params: Lista de strings en formato "clave=valor"
        
    Returns:
        Diccionario con los parámetros parseados
    """
    result = {}
    for param in params:
        if "=" in param:
            key, value = param.split("=", 1)
            result[key] = value
    return result




import argparse
import os
import sys
from aemetdata import AemetClient


# Alias de endpoints comunes
ENDPOINT_ALIASES = {
    "diarios": "valores/climatologicos/diarios/datos/fechaini/{fechaini}/fechafin/{fechafin}/todasestaciones",
    "mensuales": "valores/climatologicos/mensuales/datos/anioini/{anioini}/aniofin/{aniofin}/todasestaciones",
    "avisos": "avisos_cap/provincia/{provincia}",
    # Añade más alias según necesidades
}


def print_aliases():
    msg = ["Alias de endpoints disponibles:"]
    for alias, endpoint in ENDPOINT_ALIASES.items():
        msg.append(f"  {alias}: {endpoint}")
    msg.append("\nPuedes usar --alias <nombre> y completar los parámetros requeridos con --param clave=valor")
    print("\n".join(msg))




    import sys
    if "--list" in sys.argv:
        print_aliases()
        sys.exit(0)

    parser = argparse.ArgumentParser(
        description="Descarga datos de AEMET OpenData desde la terminal."
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        help="Endpoint completo de AEMET OpenData"
    )
    parser.add_argument(
        "--alias",
        type=str,
        help="Alias de endpoint predefinido (ej: diarios, mensuales, avisos)"
    )
    parser.add_argument(
        "--param",
        type=str,
        nargs="*",
        help="Parámetros para el alias en formato clave=valor (ej: --param fechaini=2024-01-01 fechafin=2024-01-02)"
    )
    parser.add_argument(
        "--output",
        type=str,
        required=False,
        help="Archivo de salida (si no se indica, muestra los primeros 500 caracteres en pantalla)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        required=False,
        help="API Key de AEMET OpenData (opcional, si no se indica se usa la variable de entorno AEMET_API_KEY)"
    )

    args = parser.parse_args()

    if not args.endpoint and not args.alias:
        parser.error("Debes proporcionar --endpoint o --alias (usa --list para ver opciones)")

    if args.alias:
        if args.alias not in ENDPOINT_ALIASES:
            print(f"Alias desconocido: {args.alias}")
            print_aliases()
            sys.exit(1)
        endpoint_template = ENDPOINT_ALIASES[args.alias]
        params = parse_params(args.param or [])
        try:
            endpoint = endpoint_template.format(**params)
        except KeyError as e:
            print(f"Falta el parámetro requerido: {e.args[0]}")
            print(f"Ejemplo: --param fechaini=2024-01-01 fechafin=2024-01-02")
            sys.exit(1)
    else:
        endpoint = args.endpoint

    api_key = args.api_key or os.environ.get("AEMET_API_KEY")
    if not api_key:
        print("ERROR: Debes proporcionar una API Key con --api-key o la variable de entorno AEMET_API_KEY.")
        sys.exit(1)

    client = AemetClient(api_key=api_key)
    data = client.download_data(endpoint)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"Datos guardados en {args.output}")
    else:
        print(data[:500])
        print(f"Datos guardados en {args.output}")
