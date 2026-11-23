"""Plan semanal: asignar rutinas por día, regla de descanso muscular de 48 h y rutina del día."""
import sqlite3
from datetime import date

import pytest

from pulseup.core.roles import ID_SUPERADMINISTRADOR
from tests.helpers import (
    cabeceras,
    crear_rutina,
    ejercicios_de_grupo,
    rutina_de_grupos,
    usuario_con_rol,
    usuario_con_token,
)

LUNES, MARTES, MIERCOLES, DOMINGO = 1, 2, 3, 7
# 16 de noviembre de 2026 es lunes
HOY_LUNES = date(2026, 11, 16)


@pytest.fixture
def ana(client):
    """Token de un usuario recién registrado."""
    return usuario_con_token(client)[1]


def _plan(client, token):
    r = client.get("/api/plan/", headers=cabeceras(token))
    assert r.status_code == 200
    return r.get_json()["plan"]


def _asignar(client, token, dia, id_rutina):
    return client.put(f"/api/plan/{dia}", json={"id_rutina": id_rutina}, headers=cabeceras(token))


# ---- Armar el plan --------------------------------------------------------------

def test_plan_requiere_token(client):
    assert client.get("/api/plan/").status_code == 401
    assert client.put("/api/plan/1", json={"id_rutina": 1}).status_code == 401
    assert client.delete("/api/plan/1").status_code == 401
    assert client.post("/api/plan/validar", json={}).status_code == 401
    assert client.post("/api/plan/completar").status_code == 401
    assert client.get("/api/plan/incumplidos").status_code == 401
    assert client.get("/api/calendario/").status_code == 401


def test_plan_vacio_son_siete_dias_de_descanso(client, ana):
    plan = _plan(client, ana)
    assert [d["dia_semana"] for d in plan] == [1, 2, 3, 4, 5, 6, 7]
    assert plan[0]["nombre_dia"] == "lunes" and plan[6]["nombre_dia"] == "domingo"
    assert all(d["rutina"] is None for d in plan)


def test_asignar_rutina_a_un_dia(client, ana):
    id_r = rutina_de_grupos(client, ana, "pecho", "triceps")
    r = _asignar(client, ana, LUNES, id_r)
    assert r.status_code == 200
    assert r.get_json()["dia"]["rutina"]["id"] == id_r

    lunes = _plan(client, ana)[0]
    assert lunes["rutina"]["id"] == id_r
    assert lunes["rutina"]["grupos_musculares"] == ["pecho", "triceps"]


def test_asignar_una_plantilla_del_sistema(client, ana):
    plantilla = client.get("/api/rutinas/", headers=cabeceras(ana)).get_json()["rutinas"][0]
    assert _asignar(client, ana, LUNES, plantilla["id"]).status_code == 200


def test_reemplazar_la_rutina_de_un_dia(client, ana):
    primera = rutina_de_grupos(client, ana, "pecho")
    segunda = rutina_de_grupos(client, ana, "espalda")
    _asignar(client, ana, LUNES, primera)
    assert _asignar(client, ana, LUNES, segunda).status_code == 200
    assert _plan(client, ana)[0]["rutina"]["id"] == segunda


def test_borrar_un_dia_lo_deja_en_descanso(client, ana):
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho"))
    r = client.delete(f"/api/plan/{LUNES}", headers=cabeceras(ana))
    assert r.status_code == 200
    assert _plan(client, ana)[0]["rutina"] is None


def test_rutina_de_otro_usuario_da_404(client, ana):
    _, token_luis = usuario_con_token(client, "Luis", "luis@test.com")
    ajena = rutina_de_grupos(client, token_luis, "pecho")
    assert _asignar(client, ana, LUNES, ajena).status_code == 404
    assert _asignar(client, ana, LUNES, 999999).status_code == 404


def test_datos_invalidos_dan_400(client, ana):
    id_r = rutina_de_grupos(client, ana, "pecho")
    assert _asignar(client, ana, 0, id_r).status_code == 400
    assert _asignar(client, ana, 8, id_r).status_code == 400
    assert client.put("/api/plan/1", json={}, headers=cabeceras(ana)).status_code == 400
    assert client.put("/api/plan/1", json={"id_rutina": "uno"}, headers=cabeceras(ana)).status_code == 400


def test_cada_usuario_ve_solo_su_plan(client, ana):
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho"))
    _, token_luis = usuario_con_token(client, "Luis", "luis@test.com")
    assert all(d["rutina"] is None for d in _plan(client, token_luis))


# ---- Regla de descanso muscular de 48 h -------------------------------------------

def test_mismo_grupo_lunes_y_martes_da_409(client, ana):
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho", nombre="Pecho A"))
    r = _asignar(client, ana, MARTES, rutina_de_grupos(client, ana, "pecho", nombre="Pecho B"))
    assert r.status_code == 409
    cuerpo = r.get_json()
    assert cuerpo["error"] == "Pecho ya se entrena el lunes; necesita 48 h de descanso antes de volver a trabajarlo"
    assert cuerpo["conflictos"] == [{"grupo": "pecho", "dia_semana": 1, "nombre_dia": "lunes"}]
    assert _plan(client, ana)[1]["rutina"] is None  # no se guardó


def test_el_conflicto_es_simetrico(client, ana):
    """Poner el lunes algo que choca con el martes también se bloquea."""
    _asignar(client, ana, MARTES, rutina_de_grupos(client, ana, "espalda", nombre="Espalda A"))
    r = _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "espalda", nombre="Espalda B"))
    assert r.status_code == 409
    assert r.get_json()["conflictos"][0]["nombre_dia"] == "martes"


def test_mismo_grupo_lunes_y_miercoles_es_valido(client, ana):
    id_r = rutina_de_grupos(client, ana, "pecho")
    _asignar(client, ana, LUNES, id_r)
    assert _asignar(client, ana, MIERCOLES, id_r).status_code == 200


def test_domingo_y_lunes_son_consecutivos(client, ana):
    id_r = rutina_de_grupos(client, ana, "cuadriceps")
    _asignar(client, ana, DOMINGO, id_r)
    r = _asignar(client, ana, LUNES, id_r)
    assert r.status_code == 409
    assert r.get_json()["conflictos"] == [{"grupo": "cuadriceps", "dia_semana": 7, "nombre_dia": "domingo"}]


@pytest.mark.parametrize("grupo", ["abdomen", "cardio", "pantorrillas"])
def test_grupos_exentos_se_pueden_repetir(client, ana, grupo):
    id_r = rutina_de_grupos(client, ana, grupo)
    _asignar(client, ana, LUNES, id_r)
    assert _asignar(client, ana, MARTES, id_r).status_code == 200


def test_los_musculos_secundarios_no_bloquean(client, ana):
    # Un ejercicio de pecho que trabaja tríceps de forma secundaria
    pecho = next(e for e in ejercicios_de_grupo(client, ana, "pecho") if "triceps" in e["musculos_secundarios"])
    _asignar(client, ana, LUNES, crear_rutina(client, ana, [pecho["id"]], "Pecho"))
    assert _asignar(client, ana, MARTES, rutina_de_grupos(client, ana, "triceps")).status_code == 200


def test_reemplazar_el_mismo_dia_no_se_bloquea_a_si_mismo(client, ana):
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho", nombre="Pecho A"))
    assert _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho", nombre="Pecho B")).status_code == 200


def test_un_conflicto_por_cada_grupo_repetido(client, ana):
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho", "triceps", "abdomen", nombre="Empuje"))
    r = _asignar(client, ana, MARTES, rutina_de_grupos(client, ana, "pecho", "triceps", "abdomen", nombre="Empuje 2"))
    assert r.status_code == 409
    assert [c["grupo"] for c in r.get_json()["conflictos"]] == ["pecho", "triceps"]  # abdomen está exento


def test_las_horas_de_descanso_son_configurables(client, app, ana):
    app.config["DESCANSO_MUSCULAR_HORAS"] = 24  # 1 día: martes ya no choca con lunes
    id_r = rutina_de_grupos(client, ana, "pecho")
    _asignar(client, ana, LUNES, id_r)
    assert _asignar(client, ana, MARTES, id_r).status_code == 200

    app.config["DESCANSO_MUSCULAR_HORAS"] = 72  # 3 días: miércoles choca con lunes
    r = _asignar(client, ana, MIERCOLES, id_r)
    assert r.status_code == 409
    assert "72 h" in r.get_json()["error"]


def test_validar_informa_sin_guardar(client, ana):
    id_r = rutina_de_grupos(client, ana, "pecho")
    _asignar(client, ana, LUNES, id_r)

    r = client.post("/api/plan/validar", json={"dia_semana": MARTES, "id_rutina": id_r}, headers=cabeceras(ana))
    assert r.status_code == 200
    cuerpo = r.get_json()
    assert cuerpo["valido"] is False
    assert cuerpo["conflictos"] == [{"grupo": "pecho", "dia_semana": 1, "nombre_dia": "lunes"}]

    r = client.post("/api/plan/validar", json={"dia_semana": MIERCOLES, "id_rutina": id_r}, headers=cabeceras(ana))
    assert r.get_json() == {"valido": True, "conflictos": []}

    plan = _plan(client, ana)
    assert plan[1]["rutina"] is None and plan[2]["rutina"] is None  # nada se guardó


def test_validar_con_datos_invalidos(client, ana):
    h = cabeceras(ana)
    assert client.post("/api/plan/validar", json={"dia_semana": 9, "id_rutina": 1}, headers=h).status_code == 400
    assert client.post("/api/plan/validar", json={"dia_semana": 1, "id_rutina": 999999}, headers=h).status_code == 404


# ---- Integridad con rutinas y usuarios ---------------------------------------------

def test_no_se_puede_eliminar_una_rutina_del_plan(client, ana):
    id_r = rutina_de_grupos(client, ana, "pecho")
    _asignar(client, ana, LUNES, id_r)
    r = client.delete(f"/api/rutinas/{id_r}", headers=cabeceras(ana))
    assert r.status_code == 409
    assert "La rutina está en tu plan semanal" in r.get_json()["error"]

    client.delete(f"/api/plan/{LUNES}", headers=cabeceras(ana))
    assert client.delete(f"/api/rutinas/{id_r}", headers=cabeceras(ana)).status_code == 200


def test_eliminar_usuario_borra_su_plan_y_sesiones(client, db_path, fijar_hoy):
    fijar_hoy(HOY_LUNES)
    id_ana, token_ana = usuario_con_token(client)
    _asignar(client, token_ana, LUNES, rutina_de_grupos(client, token_ana, "pecho"))
    assert client.post("/api/plan/completar", headers=cabeceras(token_ana)).status_code == 201

    _, token_super = usuario_con_rol(client, db_path, [ID_SUPERADMINISTRADOR], "Super", "super@test.com")
    assert client.delete(f"/api/users/{id_ana}", headers=cabeceras(token_super)).status_code == 200

    conn = sqlite3.connect(db_path)
    for tabla in ("plan_dia", "plan_historial", "sesion"):
        assert conn.execute(f"SELECT COUNT(*) FROM {tabla} WHERE id_usuario = ?", (id_ana,)).fetchone()[0] == 0
    conn.close()


# ---- Completar la rutina de hoy ----------------------------------------------------

def test_completar_la_rutina_de_hoy(client, ana, fijar_hoy):
    fijar_hoy(HOY_LUNES)
    id_r = rutina_de_grupos(client, ana, "pecho")
    _asignar(client, ana, LUNES, id_r)

    r = client.post("/api/plan/completar", headers=cabeceras(ana))
    assert r.status_code == 201
    sesion = r.get_json()["sesion"]
    assert sesion["fecha"] == "2026-11-16"
    # fijar_hoy también fija la hora, en la zona de Colombia (UTC-5)
    assert sesion["completada_en"] == "2026-11-16T18:30:00-05:00"
    assert sesion["nombre_dia"] == "lunes"
    assert sesion["rutina"]["id"] == id_r


def test_completar_en_dia_de_descanso_da_400(client, ana, fijar_hoy):
    fijar_hoy(HOY_LUNES)
    _asignar(client, ana, MARTES, rutina_de_grupos(client, ana, "pecho"))
    r = client.post("/api/plan/completar", headers=cabeceras(ana))
    assert r.status_code == 400
    assert r.get_json()["error"] == "Hoy es tu día de descanso"


def test_completar_dos_veces_da_409(client, ana, fijar_hoy):
    fijar_hoy(HOY_LUNES)
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho"))
    assert client.post("/api/plan/completar", headers=cabeceras(ana)).status_code == 201
    assert client.post("/api/plan/completar", headers=cabeceras(ana)).status_code == 409


def test_no_se_puede_marcar_otra_fecha(client, ana, fijar_hoy):
    fijar_hoy(HOY_LUNES)
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho"))
    h = cabeceras(ana)
    for fecha in ("2026-11-09", "2026-11-23", "ayer"):
        r = client.post("/api/plan/completar", json={"fecha": fecha}, headers=h)
        assert r.status_code == 400, fecha
    # La fecha de hoy explícita sí vale
    assert client.post("/api/plan/completar", json={"fecha": "2026-11-16"}, headers=h).status_code == 201


def test_el_dia_perdido_no_se_recupera(client, ana, fijar_hoy):
    """El lunes no se marcó; el martes (descanso) ya no hay forma de marcarlo."""
    fijar_hoy(HOY_LUNES)
    _asignar(client, ana, LUNES, rutina_de_grupos(client, ana, "pecho"))
    fijar_hoy(date(2026, 11, 17))
    assert client.post("/api/plan/completar", headers=cabeceras(ana)).status_code == 400
    r = client.post("/api/plan/completar", json={"fecha": "2026-11-16"}, headers=cabeceras(ana))
    assert r.status_code == 400


def test_no_se_puede_marcar_una_rutina_distinta_a_la_planificada(client, ana, fijar_hoy):
    fijar_hoy(HOY_LUNES)
    planificada = rutina_de_grupos(client, ana, "pecho")
    otra = rutina_de_grupos(client, ana, "espalda")
    _asignar(client, ana, LUNES, planificada)
    r = client.post("/api/plan/completar", json={"id_rutina": otra}, headers=cabeceras(ana))
    assert r.status_code == 400
    assert client.post("/api/plan/completar", json={"id_rutina": planificada}, headers=cabeceras(ana)).status_code == 201
