"""La app es solo para Colombia: "hoy" se calcula en America/Bogota, no con el reloj del servidor."""
from datetime import datetime, timezone

import pytest

from pulseup.core import tiempo
from tests.helpers import cabeceras, usuario_con_token

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


def test_habito_sin_fecha_queda_en_el_dia_de_colombia(client, reloj_fijo):
    _, token = usuario_con_token(client)
    r = client.post("/api/habitos/", json={"descripcion": "Tomar agua"}, headers=cabeceras(token))
    assert r.status_code == 201
    habitos = client.get("/api/habitos/?fecha=2026-11-22", headers=cabeceras(token)).get_json()["habitos"]
    assert [h["descripcion"] for h in habitos] == ["Tomar agua"]


def test_habito_sin_fecha_usa_hoy_sustituible(client, fijar_hoy):
    from datetime import date

    fijar_hoy(date(2026, 3, 15))
    _, token = usuario_con_token(client)
    client.post("/api/habitos/", json={"descripcion": "Caminar"}, headers=cabeceras(token))
    habitos = client.get("/api/habitos/?fecha=2026-03-15", headers=cabeceras(token)).get_json()["habitos"]
    assert len(habitos) == 1
