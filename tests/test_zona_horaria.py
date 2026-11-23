"""La app es solo para Colombia: "hoy" se calcula en America/Bogota, no con el reloj del servidor."""
from datetime import datetime, timezone

import pytest

from pulseup.core import tiempo

# 23 de noviembre a las 03:00 UTC = 22 de noviembre a las 22:00 en Colombia (UTC-5)
INSTANTE_UTC = datetime(2026, 11, 23, 3, 0, tzinfo=timezone.utc)


@pytest.fixture
def reloj_fijo(monkeypatch):
    """Fija el reloj en INSTANTE_UTC; `tiempo` lo convierte a la zona configurada."""

    class Reloj(datetime):
        @classmethod
        def now(cls, tz=None):
            return INSTANTE_UTC.astimezone(tz)

    monkeypatch.setattr(tiempo, "datetime", Reloj)


def test_hoy_usa_la_hora_de_colombia(app, reloj_fijo):
    with app.app_context():
        assert tiempo.hoy().isoformat() == "2026-11-22"  # en UTC ya sería 23


def test_la_zona_es_configurable(app, reloj_fijo):
    app.config["TZ"] = "UTC"
    with app.app_context():
        assert tiempo.hoy().isoformat() == "2026-11-23"

