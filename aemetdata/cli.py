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


def main():
    """Función principal de CLI."""
    pass
