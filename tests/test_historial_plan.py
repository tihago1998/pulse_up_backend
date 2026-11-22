"""Historial del plan: cambiar o quitar un día no reescribe el pasado del calendario."""
import sqlite3
from datetime import date

import pytest

from pulseup import inicializar_base_de_datos
from tests.helpers import cabeceras, rutina_de_grupos, usuario_con_token

LUNES, MIERCOLES = 1, 3


def d(dia):
    """Fecha de noviembre de 2026 (el 2, 9, 16, 23 y 30 son lunes)."""
    return date(2026, 11, dia)


@pytest.fixture
def ana(client):
    return usuario_con_token(client)[1]


def _asignar(client, token, dia, id_rutina):
    r = client.put(f"/api/plan/{dia}", json={"id_rutina": id_rutina}, headers=cabeceras(token))
    assert r.status_code == 200, r.get_json()


def _quitar(client, token, dia):
    assert client.delete(f"/api/plan/{dia}", headers=cabeceras(token)).status_code == 200


def _dias(client, token, mes="2026-11"):
    cal = client.get(f"/api/calendario/?mes={mes}", headers=cabeceras(token)).get_json()
    return {dia["fecha"]: dia for dia in cal["dias"]}, cal["racha"]


def _incumplidos(client, token, desde="2026-11-01"):
    r = client.get(f"/api/plan/incumplidos?desde={desde}", headers=cabeceras(token))
    return [i["fecha"] for i in r.get_json()["incumplidos"]]


def test_quitar_un_dia_no_borra_los_incumplidos_anteriores(client, ana, fijar_hoy):
    fijar_hoy(d(2))
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho", nombre="Pecho"))

    fijar_hoy(d(17))  # martes 17: los lunes 2, 9 y 16 quedaron sin marcar
    _quitar(client, ana, LUNES)

    dias, racha = _dias(client, ana)
    for lunes in ("2026-11-02", "2026-11-09", "2026-11-16"):
        assert dias[lunes]["estado"] == "incumplido", lunes
        assert dias[lunes]["rutina"]["nombre"] == "Pecho"
    assert dias["2026-11-23"]["estado"] == "descanso"  # desde que se quitó, es descanso
    assert _incumplidos(client, ana) == ["2026-11-16", "2026-11-09", "2026-11-02"]
    assert racha == {"actual": 0, "mejor": 0}


def test_quitar_hoy_deja_hoy_en_descanso(client, ana, fijar_hoy):
    fijar_hoy(d(2))
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho"))
    fijar_hoy(d(9))  # lunes 9: se quita el lunes el mismo día
    _quitar(client, ana, LUNES)

    dias, _ = _dias(client, ana)
    assert dias["2026-11-02"]["estado"] == "incumplido"
    assert dias["2026-11-09"]["estado"] == "descanso"
    assert client.post("/api/plan/completar", headers=cabeceras(ana)).status_code == 400


def test_reemplazar_la_rutina_conserva_la_anterior_en_el_pasado(client, ana, fijar_hoy):
    fijar_hoy(d(2))
    pecho = rutina_de_grupos(client, ana, "pecho", nombre="Pecho")
    espalda = rutina_de_grupos(client, ana, "espalda", nombre="Espalda")
    _asignar(client, ana, LUNES, pecho)

    fijar_hoy(d(10))  # martes 10: el lunes pasa a ser de espalda
    _asignar(client, ana, LUNES, espalda)

    dias, _ = _dias(client, ana)
    assert dias["2026-11-02"]["rutina"]["nombre"] == "Pecho"
    assert dias["2026-11-09"]["rutina"]["nombre"] == "Pecho"
    assert dias["2026-11-16"]["rutina"]["nombre"] == "Espalda"
    assert dias["2026-11-16"]["estado"] == "pendiente"


def test_reasignar_la_misma_rutina_no_reinicia_el_historial(client, ana, fijar_hoy):
    fijar_hoy(d(2))
    pecho = rutina_de_grupos(client, ana, "pecho")
    _asignar(client, ana, LUNES, pecho)
    fijar_hoy(d(10))
    _asignar(client, ana, LUNES, pecho)  # mismo valor: no es un cambio
    assert _incumplidos(client, ana) == ["2026-11-09", "2026-11-02"]


def test_cambios_el_mismo_dia_no_dejan_rastro(client, ana, fijar_hoy):
    """Asignar y quitar el mismo día equivale a no haber planificado nada."""
    fijar_hoy(d(2))
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho"))
    _quitar(client, ana, LUNES)
    fijar_hoy(d(20))
    dias, _ = _dias(client, ana)
    assert all(dia["estado"] == "descanso" for dia in dias.values())
    assert _incumplidos(client, ana) == []


def test_quitar_y_volver_a_planificar(client, ana, fijar_hoy):
    fijar_hoy(d(2))
    pecho = rutina_de_grupos(client, ana, "pecho")
    _asignar(client, ana, LUNES, pecho)
    fijar_hoy(d(3))
    _quitar(client, ana, LUNES)          # el lunes 9 queda en descanso
    fijar_hoy(d(12))
    _asignar(client, ana, LUNES, pecho)  # vuelve desde el jueves 12

    dias, _ = _dias(client, ana)
    assert dias["2026-11-02"]["estado"] == "incumplido"
    assert dias["2026-11-09"]["estado"] == "descanso"
    assert dias["2026-11-16"]["estado"] == "pendiente"


def test_la_racha_no_se_repara_quitando_el_dia_incumplido(client, ana, fijar_hoy):
    fijar_hoy(d(2))
    pecho = rutina_de_grupos(client, ana, "pecho")
    _asignar(client, ana, LUNES, pecho)
    _asignar(client, ana, MIERCOLES, pecho)
    fijar_hoy(d(2))
    assert client.post("/api/plan/completar", headers=cabeceras(ana)).status_code == 201
    fijar_hoy(d(5))  # jueves 5: el miércoles 4 quedó incumplido
    _quitar(client, ana, MIERCOLES)
    _, racha = _dias(client, ana)
    assert racha == {"actual": 0, "mejor": 1}


def test_nombre_de_rutina_eliminada_se_conserva_en_el_calendario(client, ana, fijar_hoy):
    fijar_hoy(d(2))
    id_r = rutina_de_grupos(client, ana, "pecho", nombre="Pecho viejo")
    _asignar(client, ana, LUNES, id_r)
    assert client.post("/api/plan/completar", headers=cabeceras(ana)).status_code == 201
    fijar_hoy(d(10))
    _quitar(client, ana, LUNES)
    assert client.delete(f"/api/rutinas/{id_r}", headers=cabeceras(ana)).status_code == 200

    dias, _ = _dias(client, ana)
    assert dias["2026-11-02"]["estado"] == "cumplido"
    assert dias["2026-11-02"]["rutina"] == {"id": id_r, "nombre": "Pecho viejo"}
    assert dias["2026-11-09"]["rutina"] == {"id": id_r, "nombre": "Pecho viejo"}  # incumplido


def test_migracion_crea_historial_para_planes_existentes(client, db_path, ana, fijar_hoy):
    """Bases con plan_dia creado antes de existir el historial."""
    fijar_hoy(d(20))
    id_r = rutina_de_grupos(client, ana, "pecho", nombre="Pecho")
    conn = sqlite3.connect(db_path)
    id_usuario = conn.execute("SELECT id_usuario FROM usuario").fetchone()[0]
    conn.execute(
        "INSERT INTO plan_dia (id_usuario, dia_semana, id_rutina, creado_en) VALUES (?, 1, ?, '2026-11-02')",
        (id_usuario, id_r),
    )
    conn.commit()
    conn.close()

    inicializar_base_de_datos(db_path)
    inicializar_base_de_datos(db_path)  # idempotente: no duplica

    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM plan_historial").fetchone()[0] == 1
    conn.close()
    assert _incumplidos(client, ana) == ["2026-11-16", "2026-11-09", "2026-11-02"]
