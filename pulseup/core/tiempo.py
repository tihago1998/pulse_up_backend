"""Fecha y hora "del negocio", calculadas en la zona horaria configurada (`TZ` / PULSEUP_TZ).

Quien necesite saber qué día es hoy debe llamar a `tiempo.hoy()` a través del módulo
(no con `from pulseup.core.tiempo import hoy`): así las pruebas pueden sustituir la
función y fijar la fecha sin depender del reloj real.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import current_app


def zona_horaria():
    return ZoneInfo(current_app.config["TZ"])


def ahora():
    return datetime.now(zona_horaria())


def hoy():
    return ahora().date()
