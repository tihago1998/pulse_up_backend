"""Validaciones pequeñas que comparten varios módulos."""
from datetime import datetime

from pulseup.core.errors import SolicitudInvalida


def fecha_valida(texto):
    """Acepta solo YYYY-MM-DD."""
    try:
        datetime.strptime(texto, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def exigir_fecha(texto, mensaje="Fecha inválida, usa el formato YYYY-MM-DD"):
    if not fecha_valida(texto):
        raise SolicitudInvalida(mensaje)
    return texto


def cuerpo_json(request):
    """El JSON de la petición, o un diccionario vacío si no llegó o está mal formado."""
    return request.get_json(silent=True) or {}
