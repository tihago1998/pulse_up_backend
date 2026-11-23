"""Configuración centralizada del proyecto (variables de entorno)."""
import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv

# Lee las variables del archivo .env (si existe), sin pisar las del sistema
load_dotenv()


def cargar_config(overrides=None):
    """Arma la configuración desde el entorno. `overrides` sirve para las pruebas."""
    config = {
        "SECRET_KEY": os.environ.get("PULSEUP_SECRET_KEY"),
        "DB_NAME": os.environ.get("PULSEUP_DB_NAME", "pulseup.db"),
        "HOST": os.environ.get("PULSEUP_HOST", "0.0.0.0"),
        "PORT": int(os.environ.get("PULSEUP_PORT", 5050)),
        "DEBUG": os.environ.get("PULSEUP_DEBUG", "true").lower() == "true",
        # Zona horaria con la que se decide qué día es "hoy" (plan semanal y calendario)
        "TZ": os.environ.get("PULSEUP_TZ", "America/Bogota"),
        # Descanso mínimo entre dos días que trabajan el mismo grupo muscular
        "DESCANSO_MUSCULAR_HORAS": int(os.environ.get("PULSEUP_DESCANSO_MUSCULAR_HORAS", 48)),
    }
    config.update(overrides or {})
    if not config["SECRET_KEY"]:
        raise RuntimeError(
            "Falta la variable PULSEUP_SECRET_KEY. "
            "Copia .env.example a .env y define una clave."
        )
    try:
        ZoneInfo(config["TZ"])
    except (ZoneInfoNotFoundError, ValueError):
        raise RuntimeError(
            f"Zona horaria no válida en PULSEUP_TZ: {config['TZ']!r} (ejemplo: America/Bogota)"
        )
    if config["DESCANSO_MUSCULAR_HORAS"] < 0:
        raise RuntimeError("PULSEUP_DESCANSO_MUSCULAR_HORAS no puede ser negativo")
    return config
