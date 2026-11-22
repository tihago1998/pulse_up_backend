import os
import sys
from datetime import datetime, time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("PULSEUP_SECRET_KEY", "clave-de-pruebas-de-al-menos-32-bytes!!")

from pulseup import create_app  # noqa: E402

# Hora del día que devuelve `tiempo.ahora()` cuando una prueba fija la fecha con `fijar_hoy`
HORA_FIJA = time(18, 30)


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "pulseup.db")


@pytest.fixture
def app(db_path):
    return create_app(
        {
            "SECRET_KEY": "clave-de-pruebas-de-al-menos-32-bytes!!",
            "DB_NAME": db_path,
            "TESTING": True,
        }
    )


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def fijar_hoy(monkeypatch):
    """Fija la fecha "hoy" del negocio (y la hora "ahora") sin depender del reloj real.

    Uso: `fijar_hoy(date(2026, 11, 16))`; se puede llamar varias veces para avanzar el tiempo.
    `ahora()` queda en esa fecha a la hora `HORA_FIJA`, en la zona configurada (PULSEUP_TZ),
    así `completada_en` de una sesión coincide con su fecha.
    """
    from pulseup.core import tiempo

    def fijar(fecha):
        monkeypatch.setattr(tiempo, "hoy", lambda: fecha)
        monkeypatch.setattr(
            tiempo, "ahora", lambda: datetime.combine(fecha, HORA_FIJA, tzinfo=tiempo.zona_horaria())
        )
        return fecha

    return fijar
