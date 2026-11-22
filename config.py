"""Configuración centralizada del proyecto (variables de entorno)."""
import os

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
    }
    config.update(overrides or {})
    if not config["SECRET_KEY"]:
        raise RuntimeError(
            "Falta la variable PULSEUP_SECRET_KEY. "
            "Copia .env.example a .env y define una clave."
        )
    return config
