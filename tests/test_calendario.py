"""Calendario mensual con estados, racha y lista de incumplidos."""
from datetime import date

import pytest

from tests.helpers import cabeceras, rutina_de_grupos, usuario_con_token

LUNES, MIERCOLES, VIERNES = 1, 3, 5


def d(dia):
    """Fecha de noviembre de 2026 (el 2, 9, 16, 23 y 30 son lunes)."""
    return date(2026, 11, dia)


@pytest.fixture
def ana(client):
    return usuario_con_token(client)[1]


def _asignar(client, token, dia, id_rutina):
    r = client.put(f"/api/plan/{dia}", json={"id_rutina": id_rutina}, headers=cabeceras(token))
    assert r.status_code == 200, r.get_json()


def _completar(client, token, fijar_hoy, fecha):
    fijar_hoy(fecha)
    assert client.post("/api/plan/completar", headers=cabeceras(token)).status_code == 201


def _calendario(client, token, mes="2026-11"):
    r = client.get(f"/api/calendario/?mes={mes}", headers=cabeceras(token))
    assert r.status_code == 200, r.get_json()
    return r.get_json()


def _estados(cal):
    return {dia["fecha"]: dia["estado"] for dia in cal["dias"]}


def test_estados_del_calendario(client, ana, fijar_hoy):
    # El plan se arma el lunes 9: lunes = pecho, miércoles = espalda
    fijar_hoy(d(9))
    pecho = rutina_de_grupos(client, ana, "pecho")
    espalda = rutina_de_grupos(client, ana, "espalda")
    _asignar(client, ana, LUNES, pecho)
    _asignar(client, ana, MIERCOLES, espalda)

    _completar(client, ana, fijar_hoy, d(9))   # lunes 9 cumplido
    #                                            miércoles 11 sin marcar
    _completar(client, ana, fijar_hoy, d(16))  # lunes 16 cumplido
    fijar_hoy(d(18))                           # hoy: miércoles 18, aún sin marcar

    cal = _calendario(client, ana)
    assert cal["mes"] == "2026-11"
    assert len(cal["dias"]) == 30
    estados = _estados(cal)

    assert estados["2026-11-02"] == "descanso"     # lunes previo a armar el plan
    assert estados["2026-11-09"] == "cumplido"
    assert estados["2026-11-10"] == "descanso"     # martes sin rutina
    assert estados["2026-11-11"] == "incumplido"
    assert estados["2026-11-16"] == "cumplido"
    assert estados["2026-11-18"] == "pendiente"    # hoy con rutina y sin marcar
    assert estados["2026-11-23"] == "pendiente"    # futuro con rutina
    assert estados["2026-11-24"] == "descanso"

    por_fecha = {dia["fecha"]: dia for dia in cal["dias"]}
    assert por_fecha["2026-11-09"]["rutina"]["id"] == pecho
    assert por_fecha["2026-11-11"]["rutina"]["id"] == espalda
    assert por_fecha["2026-11-10"]["rutina"] is None
    assert por_fecha["2026-11-09"]["dia_semana"] == 1


def test_dias_previos_a_armar_el_plan_no_son_incumplidos(client, ana, fijar_hoy):
    fijar_hoy(d(20))  # viernes 20: se arma el plan con el lunes
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho"))
    estados = _estados(_calendario(client, ana))
    for lunes in ("2026-11-02", "2026-11-09", "2026-11-16"):
        assert estados[lunes] == "descanso"
    assert estados["2026-11-23"] == "pendiente"


def test_mes_por_defecto_es_el_actual(client, ana, fijar_hoy):
    fijar_hoy(date(2026, 2, 10))
    r = client.get("/api/calendario/", headers=cabeceras(ana))
    assert r.status_code == 200
    cal = r.get_json()
    assert cal["mes"] == "2026-02"
    assert len(cal["dias"]) == 28
    assert all(dia["estado"] == "descanso" for dia in cal["dias"])
    assert cal["racha"] == {"actual": 0, "mejor": 0}


@pytest.mark.parametrize("mes", ["2026-13", "2026-00", "2026-1", "noviembre", "2026-11-01", "0000-01"])
def test_mes_invalido_da_400(client, ana, mes):
    r = client.get(f"/api/calendario/?mes={mes}", headers=cabeceras(ana))
    assert r.status_code == 400
    assert r.get_json()["error"] == "Mes inválido, usa el formato YYYY-MM"


def test_racha_salta_descansos_y_se_rompe_con_un_incumplido(client, ana, fijar_hoy):
    # Plan desde el lunes 2: lunes, miércoles y viernes (pecho cada 48 h o más)
    fijar_hoy(d(2))
    pecho = rutina_de_grupos(client, ana, "pecho")
    for dia in (LUNES, MIERCOLES, VIERNES):
        _asignar(client, ana, dia, pecho)

    for dia in (2, 4, 6):          # semana completa: racha de 3
        _completar(client, ana, fijar_hoy, d(dia))
    #                                 lunes 9 sin marcar -> se rompe
    for dia in (11, 13):           # nueva racha de 2
        _completar(client, ana, fijar_hoy, d(dia))

    fijar_hoy(d(14))
    assert _calendario(client, ana)["racha"] == {"actual": 2, "mejor": 3}

    # El fin de semana no rompe la racha y hoy pendiente tampoco
    _completar(client, ana, fijar_hoy, d(16))
    fijar_hoy(d(18))
    assert _calendario(client, ana)["racha"] == {"actual": 3, "mejor": 3}

    # Cuando el miércoles 18 termina sin marcar, al día siguiente la racha queda en 0
    fijar_hoy(d(19))
    assert _calendario(client, ana)["racha"] == {"actual": 0, "mejor": 3}


def test_la_racha_cuenta_aunque_el_mes_consultado_sea_otro(client, ana, fijar_hoy):
    fijar_hoy(d(30))
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho"))
    _completar(client, ana, fijar_hoy, d(30))
    cal = _calendario(client, ana, mes="2026-12")
    assert cal["mes"] == "2026-12"
    assert cal["racha"] == {"actual": 1, "mejor": 1}
    assert _estados(cal)["2026-12-07"] == "pendiente"


def test_incumplidos_recientes(client, ana, fijar_hoy):
    fijar_hoy(d(2))
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho", nombre="Pecho"))
    _asignar(client, ana, MIERCOLES, rutina_de_grupos(client, ana, "espalda", nombre="Espalda"))
    _completar(client, ana, fijar_hoy, d(4))  # solo se cumplió el miércoles 4

    fijar_hoy(d(10))  # martes 10: ayer (lunes 9) quedó incumplido
    h = cabeceras(ana)
    r = client.get("/api/plan/incumplidos", headers=h)
    assert r.status_code == 200
    assert r.get_json()["incumplidos"] == [
        {"fecha": "2026-11-09", "dia_semana": 1, "nombre_dia": "lunes",
         "rutina": {"id": r.get_json()["incumplidos"][0]["rutina"]["id"], "nombre": "Pecho"}}
    ]

    lista = client.get("/api/plan/incumplidos?desde=2026-11-01", headers=h).get_json()["incumplidos"]
    assert [i["fecha"] for i in lista] == ["2026-11-09", "2026-11-02"]  # del más reciente al más antiguo

    assert client.get("/api/plan/incumplidos?desde=ayer", headers=h).status_code == 400


def test_incumplidos_vacio_sin_plan(client, ana, fijar_hoy):
    fijar_hoy(d(10))
    r = client.get("/api/plan/incumplidos?desde=2020-01-01", headers=cabeceras(ana))
    assert r.get_json() == {"incumplidos": []}
