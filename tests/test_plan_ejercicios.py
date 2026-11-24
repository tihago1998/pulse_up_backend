"""Ejercicios del catálogo directamente en un día del plan: agregar, editar, quitar, previsualizar
avisos de 48 h (que nunca bloquean), copia de rutinas compartidas y esquema aditivo."""
import sqlite3
from datetime import date

import pytest

from pulseup import inicializar_base_de_datos
from pulseup.modules.plan import ejercicios_service as svc
from pulseup.modules.plan import service as plan_service
from tests.helpers import cabeceras, crear_rutina, rutina_de_grupos, usuario_con_token

LUNES, MARTES, MIERCOLES, JUEVES, DOMINGO = 1, 2, 3, 4, 7
HOY_LUNES = date(2026, 11, 16)  # es lunes
AVISO_PECHO_LUNES = {
    "tipo": "descanso_48h",
    "musculo": "pecho",
    "dia_conflicto": LUNES,
    "mensaje": "El lunes ya trabajas pecho: tu pecho necesita 48 horas de descanso",
}


# ---- Funciones puras ------------------------------------------------------------------------

def test_valores_por_defecto_sin_recomendacion():
    assert svc.valores_por_defecto(None) == {
        "series": 3, "repeticiones": "10", "unidad": "repeticiones", "descanso_seg": 60, "peso_kg": None,
    }


def test_valores_por_defecto_desde_la_recomendacion():
    rec = {"series_min": 3, "series_max": 4, "reps_min": 6, "reps_max": 12, "unidad": "repeticiones",
           "descanso_seg": 150, "peso_kg": 72.5}
    assert svc.valores_por_defecto(rec) == {
        "series": 4, "repeticiones": "9", "unidad": "repeticiones", "descanso_seg": 150, "peso_kg": 72.5,
    }
    cardio = {**rec, "series_max": 1, "reps_min": 30, "reps_max": 40, "unidad": "minutos", "descanso_seg": None,
              "peso_kg": None}
    assert svc.valores_por_defecto(cardio)["descanso_seg"] == 0


def test_nombres_de_rutina_del_plan():
    assert svc.nombre_rutina_para_dia(MIERCOLES, "pecho") == "Miércoles · pecho"
    assert svc.base_del_nombre("Lunes · pecho", "plan") == "pecho"
    assert svc.base_del_nombre("Full body · A", None) == "Full body · A"  # rutina del usuario: nombre completo


@pytest.mark.parametrize(
    "rutina, dias, esperado",
    [
        ({"id_usuario": 1, "origen": "plan"}, [LUNES], False),
        ({"id_usuario": 1, "origen": "plan"}, [LUNES, JUEVES], True),  # compartida con otro día
        ({"id_usuario": 1, "origen": None}, [LUNES], True),  # creada en la pantalla de rutinas
        ({"id_usuario": None, "origen": None}, [LUNES], True),  # plantilla del sistema
        ({"id_usuario": 2, "origen": "plan"}, [LUNES], True),  # de otro usuario
    ],
)
def test_cuando_se_copia_la_rutina(rutina, dias, esperado):
    assert svc.necesita_copia(rutina, 1, LUNES, dias) is esperado


def test_campos_validados():
    assert svc.campos_validados({"series": 4, "peso_kg": None, "otro": 1}, exigir_alguno=True) == {
        "series": 4, "peso_kg": None,
    }
    assert svc.campos_validados({}, exigir_alguno=False) == {}


def test_regla_pura_mismo_dia_y_exentos(app):
    grupos_por_dia = {LUNES: {"pecho", "abdomen", "cardio"}, JUEVES: {"espalda"}}
    # Mismo día: otro ejercicio de pecho el lunes no es conflicto
    assert plan_service.conflictos_entre_dias(LUNES, {"pecho"}, grupos_por_dia, 2) == []
    # Martes con pecho choca con el lunes; abdomen y cardio están exentos
    conflictos = plan_service.conflictos_entre_dias(MARTES, {"pecho", "abdomen", "cardio"}, grupos_por_dia, 2)
    assert conflictos == [{"grupo": "pecho", "dia_semana": LUNES, "nombre_dia": "lunes"}]
    assert plan_service.avisos_desde_conflictos(conflictos, 48) == [AVISO_PECHO_LUNES]


def test_mensaje_en_plural_y_con_tildes():
    assert plan_service.mensaje_aviso("gluteos", "martes", 48) == (
        "El martes ya trabajas glúteos: tus glúteos necesitan 48 horas de descanso"
    )
    assert plan_service.mensaje_aviso("triceps", "lunes", 72) == (
        "El lunes ya trabajas tríceps: tu tríceps necesita 72 horas de descanso"
    )


# ---- Apoyo para el contrato -------------------------------------------------------------------

@pytest.fixture
def ana(client, fijar_hoy):
    fijar_hoy(HOY_LUNES)
    return usuario_con_token(client)[1]


def _id(client, token, nombre):
    ejercicios = client.get("/api/ejercicios/", query_string={"q": nombre}, headers=cabeceras(token)).get_json()
    return next(e["id"] for e in ejercicios["ejercicios"] if e["nombre"] == nombre)


def _perfil(client, token, **cambios):
    cuerpo = {"fecha_nacimiento": "2001-03-10", "sexo": "hombre", "peso_kg": 80, "estatura_cm": 178,
              "nivel": "intermedio", **cambios}
    assert client.put("/api/perfil-fisico/", json=cuerpo, headers=cabeceras(token)).status_code == 200


def _agregar(client, token, dia, ejercicio_id, **campos):
    return client.post(f"/api/plan/{dia}/ejercicios", json={"ejercicio_id": ejercicio_id, **campos},
                       headers=cabeceras(token))


def _plan(client, token):
    return client.get("/api/plan/", headers=cabeceras(token)).get_json()["plan"]


def _asignar(client, token, dia, id_rutina):
    return client.put(f"/api/plan/{dia}", json={"id_rutina": id_rutina}, headers=cabeceras(token))


def _rutina(client, token, id_rutina):
    return client.get(f"/api/rutinas/{id_rutina}", headers=cabeceras(token))


# ---- Agregar ----------------------------------------------------------------------------------

def test_endpoints_nuevos_requieren_token(client):
    assert client.get("/api/plan/previsualizar?ejercicio_id=1").status_code == 401
    assert client.post("/api/plan/1/ejercicios", json={"ejercicio_id": 1}).status_code == 401
    assert client.put("/api/plan/1/ejercicios/1", json={"series": 3}).status_code == 401
    assert client.delete("/api/plan/1/ejercicios/1").status_code == 401


def test_agregar_a_dia_sin_rutina_crea_rutina_del_plan_y_la_asigna(client, ana):
    banca = _id(client, ana, "Press de banca con barra")
    r = _agregar(client, ana, LUNES, banca)
    assert r.status_code == 201
    cuerpo = r.get_json()
    assert cuerpo["rutina_copiada"] is False and cuerpo["avisos"] == []
    item = cuerpo["item"]
    assert item["ejercicio_id"] == banca and item["nombre"] == "Press de banca con barra"
    assert item["musculo_principal"] == "pecho"

    lunes = _plan(client, ana)[0]
    assert lunes["rutina"]["nombre"] == "Lunes · pecho"
    assert lunes["rutina"]["grupos_musculares"] == ["pecho"]
    assert lunes["ejercicios"] == [item]

    rutina = _rutina(client, ana, lunes["rutina"]["id"]).get_json()["rutina"]
    assert rutina["origen"] == "plan" and rutina["es_plantilla"] is False


def test_agregar_usa_el_mismo_servicio_que_put_y_respeta_el_historial(client, ana, db_path):
    _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra"))
    conn = sqlite3.connect(db_path)
    filas = conn.execute("SELECT dia_semana, nombre_rutina, vigente_desde, vigente_hasta FROM plan_historial").fetchall()
    conn.close()
    assert filas == [(LUNES, "Lunes · pecho", "2026-11-16", None)]


def test_agregar_a_dia_con_rutina_propia_del_plan(client, ana):
    _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra"))
    id_rutina = _plan(client, ana)[0]["rutina"]["id"]
    r = _agregar(client, ana, LUNES, _id(client, ana, "Aperturas con mancuernas"))
    assert r.status_code == 201 and r.get_json()["rutina_copiada"] is False
    lunes = _plan(client, ana)[0]
    assert lunes["rutina"]["id"] == id_rutina
    assert [e["nombre"] for e in lunes["ejercicios"]] == ["Press de banca con barra", "Aperturas con mancuernas"]


def test_agregar_a_rutina_compartida_copia_y_los_otros_dias_no_cambian(client, ana):
    compartida = rutina_de_grupos(client, ana, "espalda", nombre="Espalda")
    _asignar(client, ana, LUNES, compartida)
    _asignar(client, ana, JUEVES, compartida)

    r = _agregar(client, ana, LUNES, _id(client, ana, "Plancha"))
    assert r.status_code == 201 and r.get_json()["rutina_copiada"] is True

    plan = _plan(client, ana)
    lunes, jueves = plan[0], plan[3]
    assert lunes["rutina"]["id"] != compartida and lunes["rutina"]["nombre"] == "Lunes · Espalda"
    assert [e["nombre"] for e in lunes["ejercicios"]][-1] == "Plancha" and len(lunes["ejercicios"]) == 2
    assert jueves["rutina"]["id"] == compartida and len(jueves["ejercicios"]) == 1
    assert _rutina(client, ana, compartida).get_json()["rutina"]["total_ejercicios"] == 1  # original intacta


def test_rutina_creada_por_el_usuario_se_copia_aunque_este_en_un_solo_dia(client, ana):
    propia = rutina_de_grupos(client, ana, "espalda", nombre="Mi espalda")
    _asignar(client, ana, LUNES, propia)
    assert _agregar(client, ana, LUNES, _id(client, ana, "Plancha")).get_json()["rutina_copiada"] is True
    assert _rutina(client, ana, propia).get_json()["rutina"]["total_ejercicios"] == 1


def test_plantilla_del_sistema_se_copia(client, ana):
    plantilla = client.get("/api/rutinas/", headers=cabeceras(ana)).get_json()["rutinas"][0]
    _asignar(client, ana, LUNES, plantilla["id"])
    en_plantilla = {e["ejercicio"]["nombre"] for e in _rutina(client, ana, plantilla["id"]).get_json()["rutina"]["ejercicios"]}
    nuevo = next(n for n in ("Cuerda de saltar", "Plancha", "Burpees", "Remo con barra") if n not in en_plantilla)
    r = _agregar(client, ana, LUNES, _id(client, ana, nuevo))
    assert r.status_code == 201 and r.get_json()["rutina_copiada"] is True
    lunes = _plan(client, ana)[0]
    assert lunes["rutina"]["nombre"] == f"Lunes · {plantilla['nombre']}"
    assert len(lunes["ejercicios"]) == plantilla["total_ejercicios"] + 1


def test_ejercicio_duplicado_en_el_dia_da_409(client, ana):
    banca = _id(client, ana, "Press de banca con barra")
    _agregar(client, ana, LUNES, banca)
    r = _agregar(client, ana, LUNES, banca)
    assert r.status_code == 409
    assert r.get_json()["error"] == "Ese ejercicio ya está en este día"
    assert _agregar(client, ana, MIERCOLES, banca).status_code == 201  # en otro día sí


def test_valores_por_defecto_sin_perfil(client, ana):
    item = _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra")).get_json()["item"]
    assert (item["series"], item["repeticiones"], item["unidad"], item["descanso_seg"], item["peso_kg"]) == (
        3, "10", "repeticiones", 60, None,
    )


def test_valores_por_defecto_con_perfil(client, ana):
    _perfil(client, ana)  # hombre, 80 kg, 25 años, intermedio
    banca = _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra")).get_json()["item"]
    # carga_compuesto intermedio: 6-12 reps, 3-4 series, 150 s; peso estimado 72.5 kg
    assert (banca["series"], banca["repeticiones"], banca["unidad"], banca["descanso_seg"], banca["peso_kg"]) == (
        4, "9", "repeticiones", 150, 72.5,
    )
    plancha = _agregar(client, ana, LUNES, _id(client, ana, "Plancha")).get_json()["item"]
    assert (plancha["series"], plancha["repeticiones"], plancha["unidad"], plancha["peso_kg"]) == (3, "38", "segundos", None)


def test_lo_que_envia_el_usuario_gana_a_la_recomendacion(client, ana):
    _perfil(client, ana)
    item = _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra"),
                    series=2, repeticiones="5", peso_kg=None).get_json()["item"]
    assert (item["series"], item["repeticiones"], item["peso_kg"], item["descanso_seg"]) == (2, "5", None, 150)


@pytest.mark.parametrize(
    "cuerpo, mensaje",
    [
        ({}, "ejercicio_id es obligatorio y debe ser un número"),
        ({"ejercicio_id": "uno"}, "ejercicio_id es obligatorio y debe ser un número"),
        ({"ejercicio_id": 1, "series": 11}, "series debe ser un número entre 1 y 10"),
        ({"ejercicio_id": 1, "unidad": "kilos"}, "unidad no válida. Usa: repeticiones, segundos, minutos"),
    ],
)
def test_agregar_con_datos_invalidos_da_400(client, ana, cuerpo, mensaje):
    r = client.post(f"/api/plan/{LUNES}/ejercicios", json=cuerpo, headers=cabeceras(ana))
    assert r.status_code == 400 and r.get_json()["error"] == mensaje


def test_agregar_dia_o_ejercicio_inexistente_da_404(client, ana):
    assert _agregar(client, ana, 8, 1).status_code == 404
    assert _agregar(client, ana, 0, 1).status_code == 404
    r = _agregar(client, ana, LUNES, 999999)
    assert r.status_code == 404 and r.get_json()["error"] == "Ejercicio no encontrado"


# ---- Avisos de 48 h ---------------------------------------------------------------------------

def test_agregar_con_conflicto_avisa_pero_guarda(client, ana):
    _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra"))
    r = _agregar(client, ana, MARTES, _id(client, ana, "Aperturas con mancuernas"))
    assert r.status_code == 201
    assert r.get_json()["avisos"] == [AVISO_PECHO_LUNES]
    assert len(_plan(client, ana)[1]["ejercicios"]) == 1  # se guardó


def test_agregar_sin_conflicto_no_avisa(client, ana):
    _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra"))
    assert _agregar(client, ana, MIERCOLES, _id(client, ana, "Aperturas con mancuernas")).get_json()["avisos"] == []


def test_mismo_musculo_el_mismo_dia_no_avisa(client, ana):
    _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra"))
    assert _agregar(client, ana, LUNES, _id(client, ana, "Aperturas con mancuernas")).get_json()["avisos"] == []


@pytest.mark.parametrize("nombre", ["Abdominales crunch", "Burpees"])
def test_abdomen_y_cardio_no_avisan(client, ana, nombre):
    _agregar(client, ana, LUNES, _id(client, ana, nombre))
    assert _agregar(client, ana, MARTES, _id(client, ana, nombre)).get_json()["avisos"] == []


# ---- Previsualizar ----------------------------------------------------------------------------

def test_previsualizar_ejercicio_da_los_7_dias(client, ana):
    _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra"))
    r = client.get("/api/plan/previsualizar", query_string={"ejercicio_id": _id(client, ana, "Flexiones")},
                   headers=cabeceras(ana))
    assert r.status_code == 200
    dias = r.get_json()["dias"]
    assert [d["dia"] for d in dias] == [1, 2, 3, 4, 5, 6, 7]
    assert [d["tiene_rutina"] for d in dias] == [True] + [False] * 6
    con_aviso = {d["dia"]: d["avisos"] for d in dias if d["avisos"]}
    assert con_aviso == {
        MARTES: [AVISO_PECHO_LUNES],
        DOMINGO: [AVISO_PECHO_LUNES],  # domingo y lunes son consecutivos
    }
    assert _plan(client, ana)[1]["rutina"] is None  # no guarda nada


def test_previsualizar_rutina_usa_todos_sus_musculos(client, ana):
    _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra"))
    _agregar(client, ana, MIERCOLES, _id(client, ana, "Remo con barra"))
    rutina = rutina_de_grupos(client, ana, "pecho", "espalda", "abdomen", nombre="Torso")
    dias = client.get(f"/api/plan/previsualizar?rutina_id={rutina}", headers=cabeceras(ana)).get_json()["dias"]
    martes = dias[1]["avisos"]
    assert [(a["musculo"], a["dia_conflicto"]) for a in martes] == [("pecho", LUNES), ("espalda", MIERCOLES)]
    assert [a["musculo"] for a in dias[3]["avisos"]] == ["espalda"]  # jueves choca con el miércoles
    assert dias[4]["avisos"] == []  # viernes libre


def test_previsualizar_con_datos_invalidos(client, ana):
    h = cabeceras(ana)
    assert client.get("/api/plan/previsualizar", headers=h).status_code == 400
    assert client.get("/api/plan/previsualizar?ejercicio_id=1&rutina_id=1", headers=h).status_code == 400
    assert client.get("/api/plan/previsualizar?ejercicio_id=abc", headers=h).status_code == 400
    assert client.get("/api/plan/previsualizar?ejercicio_id=999999", headers=h).status_code == 404
    _, token_luis = usuario_con_token(client, "Luis", "luis@test.com")
    ajena = rutina_de_grupos(client, token_luis, "pecho")
    assert client.get(f"/api/plan/previsualizar?rutina_id={ajena}", headers=h).status_code == 404


# ---- Editar -----------------------------------------------------------------------------------

def test_editar_un_ejercicio(client, ana):
    item = _agregar(client, ana, LUNES, _id(client, ana, "Plancha")).get_json()["item"]
    r = client.put(f"/api/plan/{LUNES}/ejercicios/{item['item_id']}",
                   json={"series": 4, "repeticiones": "45", "unidad": "segundos", "descanso_seg": 30},
                   headers=cabeceras(ana))
    assert r.status_code == 200
    cuerpo = r.get_json()
    assert cuerpo["rutina_copiada"] is False
    assert {k: cuerpo["item"][k] for k in ("item_id", "series", "repeticiones", "unidad", "descanso_seg")} == {
        "item_id": item["item_id"], "series": 4, "repeticiones": "45", "unidad": "segundos", "descanso_seg": 30,
    }
    assert _plan(client, ana)[0]["ejercicios"] == [cuerpo["item"]]


def test_editar_peso_y_volver_a_null(client, ana):
    item = _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra")).get_json()["item"]
    url = f"/api/plan/{LUNES}/ejercicios/{item['item_id']}"
    assert client.put(url, json={"peso_kg": 62.5}, headers=cabeceras(ana)).get_json()["item"]["peso_kg"] == 62.5
    assert client.put(url, json={"peso_kg": None}, headers=cabeceras(ana)).get_json()["item"]["peso_kg"] is None


@pytest.mark.parametrize(
    "cuerpo, mensaje",
    [
        ({}, "Envía al menos uno de: series, repeticiones, peso_kg, unidad, descanso_seg"),
        ({"series": 0}, "series debe ser un número entre 1 y 10"),
        ({"series": 11}, "series debe ser un número entre 1 y 10"),
        ({"peso_kg": -1}, "peso_kg debe ser un número entre 0 y 500, o null"),
        ({"peso_kg": 501}, "peso_kg debe ser un número entre 0 y 500, o null"),
        ({"peso_kg": "50"}, "peso_kg debe ser un número entre 0 y 500, o null"),
        ({"descanso_seg": 601}, "descanso_seg debe ser un número entre 0 y 600"),
        ({"unidad": "horas"}, "unidad no válida. Usa: repeticiones, segundos, minutos"),
        ({"repeticiones": ""}, "repeticiones es obligatorio (por ejemplo 8-12, o 30 si la unidad es segundos)"),
    ],
)
def test_editar_con_datos_invalidos_da_400(client, ana, cuerpo, mensaje):
    item = _agregar(client, ana, LUNES, _id(client, ana, "Plancha")).get_json()["item"]
    r = client.put(f"/api/plan/{LUNES}/ejercicios/{item['item_id']}", json=cuerpo, headers=cabeceras(ana))
    assert r.status_code == 400 and r.get_json()["error"] == mensaje


def test_editar_item_de_otro_dia_o_inexistente_da_404(client, ana):
    item = _agregar(client, ana, LUNES, _id(client, ana, "Plancha")).get_json()["item"]
    _agregar(client, ana, MIERCOLES, _id(client, ana, "Burpees"))
    h = cabeceras(ana)
    assert client.put(f"/api/plan/{MIERCOLES}/ejercicios/{item['item_id']}", json={"series": 2}, headers=h).status_code == 404
    assert client.put(f"/api/plan/{MARTES}/ejercicios/{item['item_id']}", json={"series": 2}, headers=h).status_code == 404
    assert client.put(f"/api/plan/{LUNES}/ejercicios/999999", json={"series": 2}, headers=h).status_code == 404
    assert client.put(f"/api/plan/9/ejercicios/{item['item_id']}", json={"series": 2}, headers=h).status_code == 404


def test_no_se_tocan_rutinas_de_otro_usuario(client, ana):
    _, token_luis = usuario_con_token(client, "Luis", "luis@test.com")
    item_luis = _agregar(client, token_luis, LUNES, _id(client, token_luis, "Plancha")).get_json()["item"]
    _agregar(client, ana, LUNES, _id(client, ana, "Burpees"))
    h = cabeceras(ana)
    assert client.put(f"/api/plan/{LUNES}/ejercicios/{item_luis['item_id']}", json={"series": 1}, headers=h).status_code == 404
    assert client.delete(f"/api/plan/{LUNES}/ejercicios/{item_luis['item_id']}", headers=h).status_code == 404
    assert _plan(client, token_luis)[0]["ejercicios"] == [item_luis]


def test_editar_en_rutina_compartida_copia(client, ana):
    compartida = rutina_de_grupos(client, ana, "espalda", nombre="Espalda")
    _asignar(client, ana, LUNES, compartida)
    _asignar(client, ana, JUEVES, compartida)
    item = _plan(client, ana)[0]["ejercicios"][0]
    r = client.put(f"/api/plan/{LUNES}/ejercicios/{item['item_id']}", json={"series": 5}, headers=cabeceras(ana))
    assert r.status_code == 200
    cuerpo = r.get_json()
    assert cuerpo["rutina_copiada"] is True
    assert cuerpo["item"]["item_id"] != item["item_id"] and cuerpo["item"]["series"] == 5
    plan = _plan(client, ana)
    assert plan[0]["ejercicios"][0]["series"] == 5
    assert plan[3]["rutina"]["id"] == compartida and plan[3]["ejercicios"][0]["series"] == 3


# ---- Quitar -----------------------------------------------------------------------------------

def test_quitar_un_ejercicio(client, ana):
    primero = _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra")).get_json()["item"]
    _agregar(client, ana, LUNES, _id(client, ana, "Plancha"))
    r = client.delete(f"/api/plan/{LUNES}/ejercicios/{primero['item_id']}", headers=cabeceras(ana))
    assert r.status_code == 200
    cuerpo = r.get_json()
    assert cuerpo["dia_en_descanso"] is False and cuerpo["rutina_copiada"] is False
    assert [e["nombre"] for e in cuerpo["dia"]["ejercicios"]] == ["Plancha"]


def test_quitar_el_ultimo_borra_la_rutina_del_plan_y_deja_descanso(client, ana, db_path):
    item = _agregar(client, ana, LUNES, _id(client, ana, "Plancha")).get_json()["item"]
    id_rutina = _plan(client, ana)[0]["rutina"]["id"]
    r = client.delete(f"/api/plan/{LUNES}/ejercicios/{item['item_id']}", headers=cabeceras(ana))
    assert r.status_code == 200
    assert r.get_json()["dia_en_descanso"] is True
    assert r.get_json()["dia"] == {"dia_semana": 1, "nombre_dia": "lunes", "rutina": None, "ejercicios": []}
    assert _plan(client, ana)[0]["rutina"] is None
    assert _rutina(client, ana, id_rutina).status_code == 404  # la rutina vacía se eliminó
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM plan_historial").fetchone()[0] == 0  # empezó hoy: no aplicó a días pasados
    conn.close()


def test_quitar_de_rutina_compartida_copia_y_no_toca_otros_dias(client, ana):
    compartida = crear_rutina(client, ana, [_id(client, ana, "Plancha"), _id(client, ana, "Burpees")], "Core")
    _asignar(client, ana, LUNES, compartida)
    _asignar(client, ana, JUEVES, compartida)
    item = _plan(client, ana)[0]["ejercicios"][0]
    r = client.delete(f"/api/plan/{LUNES}/ejercicios/{item['item_id']}", headers=cabeceras(ana))
    assert r.get_json()["rutina_copiada"] is True
    plan = _plan(client, ana)
    assert [e["nombre"] for e in plan[0]["ejercicios"]] == ["Burpees"]
    assert len(plan[3]["ejercicios"]) == 2 and plan[3]["rutina"]["id"] == compartida


def test_quitar_el_unico_ejercicio_de_rutina_del_usuario_no_la_borra(client, ana):
    propia = crear_rutina(client, ana, [_id(client, ana, "Plancha")], "Mi core")
    _asignar(client, ana, LUNES, propia)
    item = _plan(client, ana)[0]["ejercicios"][0]
    r = client.delete(f"/api/plan/{LUNES}/ejercicios/{item['item_id']}", headers=cabeceras(ana))
    assert r.get_json()["dia_en_descanso"] is True
    assert _rutina(client, ana, propia).get_json()["rutina"]["total_ejercicios"] == 1  # la del usuario sigue igual


def test_quitar_item_inexistente_da_404(client, ana):
    assert client.delete(f"/api/plan/{LUNES}/ejercicios/1", headers=cabeceras(ana)).status_code == 404


# ---- Hoy ya cumplido --------------------------------------------------------------------------

def _hoy_en_calendario(client, token):
    dias = client.get("/api/calendario/?mes=2026-11", headers=cabeceras(token)).get_json()["dias"]
    return next(d for d in dias if d["fecha"] == HOY_LUNES.isoformat())


def test_cambiar_el_dia_de_hoy_ya_cumplido_no_deshace_el_cumplimiento(client, ana):
    item = _agregar(client, ana, LUNES, _id(client, ana, "Plancha")).get_json()["item"]
    assert client.post("/api/plan/completar", headers=cabeceras(ana)).status_code == 201

    assert _agregar(client, ana, LUNES, _id(client, ana, "Burpees")).status_code == 201
    assert client.put(f"/api/plan/{LUNES}/ejercicios/{item['item_id']}", json={"series": 1},
                      headers=cabeceras(ana)).status_code == 200
    assert _hoy_en_calendario(client, ana)["estado"] == "cumplido"
    assert client.post("/api/plan/completar", headers=cabeceras(ana)).status_code == 409  # sigue marcado


def test_vaciar_el_dia_de_hoy_cumplido_conserva_la_rutina_y_el_cumplimiento(client, ana):
    item = _agregar(client, ana, LUNES, _id(client, ana, "Plancha")).get_json()["item"]
    id_rutina = _plan(client, ana)[0]["rutina"]["id"]
    client.post("/api/plan/completar", headers=cabeceras(ana))

    r = client.delete(f"/api/plan/{LUNES}/ejercicios/{item['item_id']}", headers=cabeceras(ana))
    assert r.get_json()["dia_en_descanso"] is True
    hoy = _hoy_en_calendario(client, ana)
    assert hoy["estado"] == "cumplido"
    assert hoy["rutina"] == {"id": id_rutina, "nombre": "Lunes · abdomen"}  # no se pierde el nombre


# ---- GET /api/plan y rutinas existentes ---------------------------------------------------------

def test_get_plan_trae_ejercicios_en_cada_dia(client, ana):
    _agregar(client, ana, LUNES, _id(client, ana, "Press de banca con barra"))
    _asignar(client, ana, MIERCOLES, rutina_de_grupos(client, ana, "espalda"))
    plan = _plan(client, ana)
    assert all("ejercicios" in d for d in plan)
    assert [len(d["ejercicios"]) for d in plan] == [1, 0, 1, 0, 0, 0, 0]
    assert set(plan[0]["ejercicios"][0]) == {
        "item_id", "ejercicio_id", "nombre", "musculo_principal", "imagen_miniatura", "series", "repeticiones",
        "unidad", "peso_kg", "descanso_seg",
    }
    # Lo de antes sigue igual
    assert set(plan[0]) == {"dia_semana", "nombre_dia", "rutina", "ejercicios"}
    assert set(plan[0]["rutina"]) == {"id", "nombre", "grupos_musculares"}


def test_rutinas_existentes_sin_peso_ni_unidad_siguen_funcionando(client, ana):
    id_r = crear_rutina(client, ana, [_id(client, ana, "Plancha")])
    rutina = _rutina(client, ana, id_r).get_json()["rutina"]
    assert rutina["origen"] is None
    assert rutina["ejercicios"][0]["peso_kg"] is None and rutina["ejercicios"][0]["unidad"] == "repeticiones"


def test_rutinas_aceptan_peso_y_unidad_opcionales(client, ana):
    cuerpo = {"nombre": "Con peso", "ejercicios": [
        {"id_ejercicio": _id(client, ana, "Press de banca con barra"), "series": 3, "repeticiones": "8", "peso_kg": 60},
        {"id_ejercicio": _id(client, ana, "Plancha"), "series": 3, "repeticiones": "30", "unidad": "segundos"},
    ]}
    r = client.post("/api/rutinas/", json=cuerpo, headers=cabeceras(ana))
    assert r.status_code == 201
    ejercicios = _rutina(client, ana, r.get_json()["id"]).get_json()["rutina"]["ejercicios"]
    assert [(e["peso_kg"], e["unidad"]) for e in ejercicios] == [(60.0, "repeticiones"), (None, "segundos")]

    malo = {"nombre": "Mala", "ejercicios": [{**cuerpo["ejercicios"][0], "unidad": "kilos"}]}
    assert client.post("/api/rutinas/", json=malo, headers=cabeceras(ana)).status_code == 400


# ---- Esquema aditivo ---------------------------------------------------------------------------

def test_base_con_esquema_viejo_recibe_las_columnas_sin_perder_datos(tmp_path):
    db = str(tmp_path / "vieja.db")
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE rutina (id INTEGER PRIMARY KEY AUTOINCREMENT, id_usuario INTEGER, nombre TEXT NOT NULL,
            descripcion TEXT NOT NULL DEFAULT '', objetivo TEXT NOT NULL, nivel TEXT NOT NULL,
            duracion_min INTEGER NOT NULL DEFAULT 45);
        CREATE TABLE rutina_ejercicio (id INTEGER PRIMARY KEY AUTOINCREMENT, id_rutina INTEGER NOT NULL,
            id_ejercicio INTEGER NOT NULL, orden INTEGER NOT NULL, series INTEGER NOT NULL,
            repeticiones TEXT NOT NULL, descanso_seg INTEGER NOT NULL DEFAULT 60, UNIQUE (id_rutina, orden));
        INSERT INTO rutina (id_usuario, nombre, objetivo, nivel) VALUES (7, 'Vieja', 'general', 'principiante');
        INSERT INTO rutina_ejercicio (id_rutina, id_ejercicio, orden, series, repeticiones) VALUES (1, 1, 1, 3, '12');
        """
    )
    conn.commit()
    conn.close()

    inicializar_base_de_datos(db)
    inicializar_base_de_datos(db)  # idempotente

    conn = sqlite3.connect(db)
    columnas_item = {f[1] for f in conn.execute("PRAGMA table_info(rutina_ejercicio)")}
    columnas_rutina = {f[1] for f in conn.execute("PRAGMA table_info(rutina)")}
    assert {"peso_kg", "unidad"} <= columnas_item and "origen" in columnas_rutina
    assert conn.execute("SELECT series, repeticiones, peso_kg, unidad FROM rutina_ejercicio WHERE id_rutina = 1").fetchone() == (
        3, "12", None, "repeticiones",
    )
    assert conn.execute("SELECT nombre, origen FROM rutina WHERE id = 1").fetchone() == ("Vieja", None)
    conn.close()
