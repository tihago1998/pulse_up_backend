"""Conexión a SQLite. El archivo se toma de la configuración (`DB_NAME`)."""
import sqlite3
from contextlib import contextmanager

from flask import current_app


@contextmanager
def conexion():
    """Abre una conexión, confirma los cambios al salir bien y revierte si algo falla."""
    conn = sqlite3.connect(current_app.config["DB_NAME"])
    # Permite leer las columnas por nombre (fila["nombre"]) en vez de por posición
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
