"""Calorías aproximadas (MET del Compendium), resumen de recomendación en el listado de ejercicios,
precaución para ejercicios avanzados y calorías en el plan, al completar y en el calendario."""
import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest

from pulseup.core.esquema import crear_esquema
from pulseup.core.semillas import sembrar_met
from pulseup.modules.calorias import service as cal
from pulseup.modules.recomendaciones import service as rec
from tests.helpers import cabeceras, usuario_con_token

URL = "/api/ejercicios/"
LUNES = 1
HOY_LUNES = date(2026, 11, 16)
NOTA = "Estimación aproximada: el gasto real varía según la persona y la intensidad."
SEMILLA = json.loads(
    (Path(__file__).resolve().parent.parent / "pulseup" / "seeds" / "met_ejercicios.json").read_text(encoding="utf-8")
)
CAMPOS_RESUMEN = {"nivel", "series", "repeticiones", "unidad", "peso_kg", "descanso_seg", "calorias_aprox", "precaucion"}


# ---- Fórmula (casos calculados a mano) --------------------------------------------------------

def test_cardio_30_min_met_8_peso_70_son_280():
    # 8 MET × 70 kg × 0.5 h = 280 kcal
    assert cal.calorias_ejercicio(8, 70, 1, "30", "minutos", None) == 280


def test_formula_bruta_sin_redondeo():
    assert cal.kcal_brutas(8, 70, 0.5) == pytest.approx(280)
    assert cal.MET_REPOSO_A_RESTAR == 0  # bruta: no se resta el MET de reposo


@pytest.mark.parametrize("kcal, esperado", [(0.4, 5), (2, 5), (7.4, 5), (7.5, 10), (12.6, 15), (94.4, 95), (280, 280)])
def test_redondeo_a_multiplos_de_5_con_minimo_5(kcal, esperado):
    assert cal.redondear_kcal(kcal) == esperado


def test_tiempo_con_descanso_en_repeticiones():
    # 3 series × (10 reps × 3 s + 60 s) = 270 s = 0.075 h
    assert cal.duracion_horas(3, "10", "repeticiones", 60) == pytest.approx(0.075)
    # 6 MET × 80 kg × 0.075 h = 36 -> 35
    assert cal.calorias_ejercicio(6, 80, 3, "10", "repeticiones", 60) == 35


def test_tiempo_en_segundos_suma_descanso():
    # 3 × (30 s + 45 s) = 225 s; 2.8 × 80 × 0.0625 = 14 -> 15
    assert cal.duracion_horas(3, "30", "segundos", 45) == pytest.approx(0.0625)
    assert cal.calorias_ejercicio(2.8, 80, 3, "30", "segundos", 45) == 15


def test_tiempo_en_minutos_no_suma_descanso():
    assert cal.duracion_horas(2, "20", "minutos", 90) == pytest.approx(20 * 2 / 60)


@pytest.mark.parametrize("texto, esperado", [("8-12", 10), ("8 - 12", 10), ("8–11", 9.5), ("10", 10), (12, 12),
                                             ("al fallo", None), (None, None), ("", None)])
def test_rango_de_repeticiones_usa_el_punto_medio(texto, esperado):
    assert cal.valor_repeticiones(texto) == esperado


def test_rango_de_repeticiones_en_el_calculo():
    # "8-12" -> 10 reps, igual que "10"
    assert cal.calorias_ejercicio(3.5, 70, 3, "8-12", "repeticiones", 90) == cal.calorias_ejercicio(
        3.5, 70, 3, "10", "repeticiones", 90
    )


def test_sin_peso_o_sin_met_es_null():
    assert cal.calorias_ejercicio(6, None, 3, "10", "repeticiones", 60) is None
    assert cal.calorias_ejercicio(None, 80, 3, "10", "repeticiones", 60) is None
    assert cal.calorias_ejercicio(6, 80, 3, "al fallo", "repeticiones", 60) is None


def test_sin_tope_de_113_kg():
    # Con 150 kg reales: 6 × 150 × 0.075 = 67.5 -> 70 (con tope serían 50.85 -> 50)
    assert cal.calorias_ejercicio(6, 150, 3, "10", "repeticiones", 60) == 70


def test_total_ignora_los_desconocidos():
    assert cal.total([35, None, 15]) == 50
    assert cal.total([None, None]) is None
    assert cal.total([]) is None


# ---- Precaución ------------------------------------------------------------------------------

def test_precaucion_avanzado_y_principiante_menciona_la_variante():
    texto = rec.precaucion_para("avanzado", "principiante", "Elevación de rodillas colgado.")
    assert texto.startswith(rec.PRECAUCION_AVANZADO)
    assert "Elevación de rodillas colgado." in texto
    assert rec.precaucion_para("avanzado", "principiante", None) == rec.PRECAUCION_AVANZADO


@pytest.mark.parametrize("ejercicio, usuario", [("avanzado", "intermedio"), ("avanzado", "avanzado"),
                                                ("intermedio", "principiante"), ("principiante", "principiante")])
def test_precaucion_en_los_demas_casos_es_null(ejercicio, usuario):
    assert rec.precaucion_para(ejercicio, usuario, "algo") is None


# ---- Semilla MET -------------------------------------------------------------------------------

def test_semilla_cubre_los_150_con_valores_de_su_categoria():
    ejercicios = SEMILLA["ejercicios"]
    assert len(ejercicios) == len({e["nombre"] for e in ejercicios}) == 150
    for e in ejercicios:
        categoria = SEMILLA["categorias"][e["categoria"]]
        assert (e["met"], e["codigo_compendio"]) == (categoria["met"], categoria["codigo_compendio"])
        assert isinstance(e["verificado"], bool)
    # La bicicleta estática (Compendium 2011) queda por verificar
    bici = next(e for e in ejercicios if e["nombre"] == "Bicicleta estática")
    assert (bici["met"], bici["codigo_compendio"], bici["verificado"]) == (6.8, "02015", False)
    # No todo cae en 3.5
    assert len({e["met"] for e in ejercicios}) >= 8


def _met_de_la_base(conn):
    return conn.execute("SELECT id, nombre, met, codigo_compendio FROM ejercicio ORDER BY id").fetchall()


def test_semilla_aplicada_e_idempotente(app, db_path):
    conn = sqlite3.connect(db_path)
    antes = _met_de_la_base(conn)
    assert len(antes) == 150
    assert all(met is not None and codigo for _, _, met, codigo in antes)
    sembrar_met(conn)
    sembrar_met(conn)
    conn.commit()
    assert _met_de_la_base(conn) == antes  # ni duplica ni cambia
    conn.close()


def test_columnas_nuevas_aditivas(app, db_path):
    conn = sqlite3.connect(db_path)
    columnas = lambda tabla: {f[1] for f in conn.execute(f"PRAGMA table_info({tabla})")}  # noqa: E731
    assert {"met", "codigo_compendio"} <= columnas("ejercicio")
    assert "calorias_aprox" in columnas("sesion")
    conn.row_factory = sqlite3.Row
    crear_esquema(conn)  # correrlo otra vez no falla
    conn.close()


def test_esquema_viejo_recibe_las_columnas(tmp_path):
    conn = sqlite3.connect(str(tmp_path / "vieja.db"))
    conn.execute("CREATE TABLE sesion (id INTEGER PRIMARY KEY, id_usuario INTEGER NOT NULL, fecha TEXT NOT NULL,"
                 " id_rutina INTEGER NOT NULL, completada_en TEXT NOT NULL)")
    conn.execute("INSERT INTO sesion (id_usuario, fecha, id_rutina, completada_en) VALUES (1, '2026-11-02', 1, 'x')")
    conn.row_factory = sqlite3.Row
    crear_esquema(conn)
    assert conn.execute("SELECT calorias_aprox FROM sesion").fetchone()[0] is None  # los datos viejos siguen
    conn.close()


# ---- API: detalle y listado ---------------------------------------------------------------------

@pytest.fixture
def token(client, fijar_hoy):
    fijar_hoy(HOY_LUNES)
    return usuario_con_token(client)[1]


def _perfil(client, token, **cambios):
    cuerpo = {"fecha_nacimiento": "2001-03-10", "sexo": "hombre", "peso_kg": 80, "estatura_cm": 178,
              "nivel": "intermedio", **cambios}
    r = client.put("/api/perfil-fisico/", json=cuerpo, headers=cabeceras(token))
    assert r.status_code == 200, r.get_json()


def _lista(client, token, **query):
    r = client.get(URL, query_string=query, headers=cabeceras(token))
    assert r.status_code == 200, r.get_json()
    return r.get_json()


def _por_nombre(cuerpo, nombre):
    return next(e for e in cuerpo["ejercicios"] if e["nombre"] == nombre)


def _detalle(client, token, nombre):
    id_ejercicio = _por_nombre(_lista(client, token, q=nombre), nombre)["id"]
    return client.get(f"{URL}{id_ejercicio}", headers=cabeceras(token)).get_json()["ejercicio"]


def test_detalle_trae_calorias_y_nota(client, token):
    _perfil(client, token)
    recomendacion = _detalle(client, token, "Press de banca con barra")["recomendacion"]
    # 6 MET (02050) × 80 kg × 4 × (9 reps × 3 s + 150 s) / 3600 = 94.4 -> 95
    assert recomendacion["calorias_aprox"] == 95
    assert recomendacion["calorias_nota"] == NOTA
    assert recomendacion["precaucion"] is None


def test_detalle_sin_met_calorias_null(client, token, db_path):
    _perfil(client, token)
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE ejercicio SET met = NULL WHERE nombre = 'Press de banca con barra'")
    conn.commit()
    conn.close()
    recomendacion = _detalle(client, token, "Press de banca con barra")["recomendacion"]
    assert recomendacion["calorias_aprox"] is None
    assert recomendacion["series_max"] == 4  # el resto de la recomendación no cambia


def test_detalle_precaucion_para_principiante_en_ejercicio_avanzado(client, token):
    _perfil(client, token, nivel="principiante")
    precaucion = _detalle(client, token, "Dominadas")["recomendacion"]["precaucion"]
    assert precaucion.startswith(rec.PRECAUCION_AVANZADO)
    assert "Dominadas asistidas con banda elástica" in precaucion
    assert _detalle(client, token, "Flexiones")["recomendacion"]["precaucion"] is None


def test_listado_con_perfil_trae_resumen_en_cada_ejercicio(client, token):
    _perfil(client, token)
    cuerpo = _lista(client, token)
    assert cuerpo["recomendacion_motivo"] is None
    assert cuerpo["calorias_nota"] == NOTA
    assert all(set(e["recomendacion_resumen"]) == CAMPOS_RESUMEN for e in cuerpo["ejercicios"])
    assert _por_nombre(cuerpo, "Press de banca con barra")["recomendacion_resumen"] == {
        "nivel": "intermedio", "series": 4, "repeticiones": "9", "unidad": "repeticiones", "peso_kg": 72.5,
        "descanso_seg": 150, "calorias_aprox": 95, "precaucion": None,
    }
    # Cardio: 1 serie de 35 min sin descanso; 9 MET × 80 kg × 35/60 h = 420
    assert _por_nombre(cuerpo, "Cuerda de saltar")["recomendacion_resumen"] == {
        "nivel": "intermedio", "series": 1, "repeticiones": "35", "unidad": "minutos", "peso_kg": None,
        "descanso_seg": 0, "calorias_aprox": 420, "precaucion": None,
    }


def test_listado_resumen_coincide_con_el_detalle(client, token):
    _perfil(client, token, nivel="principiante")
    resumen = _por_nombre(_lista(client, token, q="Dominadas"), "Dominadas")["recomendacion_resumen"]
    detalle = _detalle(client, token, "Dominadas")["recomendacion"]
    assert resumen["calorias_aprox"] == detalle["calorias_aprox"]
    assert resumen["precaucion"] == detalle["precaucion"] is not None
    assert resumen["series"] == detalle["series_max"]


def test_listado_paginado_tambien_trae_resumen(client, token):
    _perfil(client, token)
    cuerpo = _lista(client, token, limit=3)
    assert all(e["recomendacion_resumen"] is not None for e in cuerpo["items"])
    assert cuerpo["items"] == cuerpo["ejercicios"]


def test_listado_sin_perfil_resumen_null_y_motivo(client, token):
    cuerpo = _lista(client, token)
    assert all(e["recomendacion_resumen"] is None for e in cuerpo["ejercicios"])
    assert cuerpo["recomendacion_motivo"] == "Completa tu perfil físico para ver tu recomendación y tus calorías"
    assert cuerpo["total"] == 150


def test_listado_ejercicio_sin_regla_resumen_null(client, token, db_path):
    _perfil(client, token)
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE ejercicio SET tipo_recomendacion = NULL WHERE nombre = 'Flexiones'")
    conn.commit()
    conn.close()
    cuerpo = _lista(client, token, q="Flexiones")
    assert _por_nombre(cuerpo, "Flexiones")["recomendacion_resumen"] is None
    assert _por_nombre(cuerpo, "Flexiones abiertas")["recomendacion_resumen"] is not None
    assert cuerpo["recomendacion_motivo"] is None


def test_listado_carga_perfil_y_reglas_una_sola_vez(client, token, monkeypatch):
    _perfil(client, token)
    from pulseup.modules.perfil_fisico import repository as perfil_repo

    llamadas = {"perfil": 0}
    buscar_original = perfil_repo.buscar

    def contar(conn, id_usuario):
        llamadas["perfil"] += 1
        return buscar_original(conn, id_usuario)

    def prohibido(*_):
        raise AssertionError("no debe consultar una regla por ejercicio")

    monkeypatch.setattr(perfil_repo, "buscar", contar)
    monkeypatch.setattr(rec.repo, "regla", prohibido)
    monkeypatch.setattr(rec.repo, "ratio", prohibido)
    assert len(_lista(client, token)["ejercicios"]) == 150
    assert llamadas["perfil"] == 1


def test_filtro_nivel_sigue_funcionando(client, token):
    cuerpo = _lista(client, token, nivel="avanzado")
    assert cuerpo["total"] > 0 and all(e["nivel"] == "avanzado" for e in cuerpo["ejercicios"])


# ---- API: plan, completar y calendario ----------------------------------------------------------

def _agregar(client, token, nombre, **valores):
    id_ejercicio = _por_nombre(_lista(client, token, q=nombre), nombre)["id"]
    r = client.post(f"/api/plan/{LUNES}/ejercicios", json={"ejercicio_id": id_ejercicio, **valores},
                    headers=cabeceras(token))
    assert r.status_code == 201, r.get_json()
    return r.get_json()


def _armar_lunes(client, token):
    # Press de banca: 6 MET × 80 × 3 × (30 + 60) s = 36 -> 35; Plancha: 2.8 × 80 × 3 × (30 + 45) s = 14 -> 15
    _agregar(client, token, "Press de banca con barra", series=3, repeticiones="10", unidad="repeticiones",
             descanso_seg=60)
    _agregar(client, token, "Plancha", series=3, repeticiones="30", unidad="segundos", descanso_seg=45)


def test_plan_calorias_por_ejercicio_y_total_del_dia(client, token):
    _perfil(client, token)
    _armar_lunes(client, token)
    cuerpo = client.get("/api/plan/", headers=cabeceras(token)).get_json()
    lunes = cuerpo["plan"][0]
    assert [e["calorias_aprox"] for e in lunes["ejercicios"]] == [35, 15]
    assert lunes["calorias_dia_aprox"] == 50
    assert cuerpo["plan"][1]["calorias_dia_aprox"] is None  # descanso
    assert cuerpo["calorias_nota"] == NOTA


def test_plan_usa_los_valores_reales_editados(client, token):
    _perfil(client, token)
    item = _agregar(client, token, "Press de banca con barra", series=3, repeticiones="10", descanso_seg=60)["item"]
    assert item["calorias_aprox"] == 35
    r = client.put(f"/api/plan/{LUNES}/ejercicios/{item['item_id']}", json={"series": 6}, headers=cabeceras(token))
    assert r.get_json()["item"]["calorias_aprox"] == 70  # 6 × 80 × 6 × 90 s / 3600 = 72 -> 70
    assert client.get("/api/plan/", headers=cabeceras(token)).get_json()["plan"][0]["calorias_dia_aprox"] == 70


def test_plan_sin_perfil_calorias_null(client, token):
    _armar_lunes(client, token)
    lunes = client.get("/api/plan/", headers=cabeceras(token)).get_json()["plan"][0]
    assert [e["calorias_aprox"] for e in lunes["ejercicios"]] == [None, None]
    assert lunes["calorias_dia_aprox"] is None


def test_completar_guarda_las_calorias_del_dia(client, token, db_path):
    _perfil(client, token)
    _armar_lunes(client, token)
    r = client.post("/api/plan/completar", headers=cabeceras(token))
    assert r.status_code == 201
    assert r.get_json()["sesion"]["calorias_aprox"] == 50
    assert r.get_json()["calorias_nota"] == NOTA
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT calorias_aprox FROM sesion").fetchone()[0] == 50
    conn.close()


def test_completar_sin_perfil_guarda_null(client, token):
    _armar_lunes(client, token)
    assert client.post("/api/plan/completar", headers=cabeceras(token)).get_json()["sesion"]["calorias_aprox"] is None


def test_calendario_muestra_las_calorias_guardadas(client, token, fijar_hoy):
    _perfil(client, token)
    _armar_lunes(client, token)
    client.post("/api/plan/completar", headers=cabeceras(token))
    # Cambiar el plan después no cambia lo guardado en la sesión
    _agregar(client, token, "Cuerda de saltar", series=1, repeticiones="30", unidad="minutos", descanso_seg=0)
    fijar_hoy(date(2026, 11, 24))  # el lunes 23 queda incumplido
    cuerpo = client.get("/api/calendario/?mes=2026-11", headers=cabeceras(token)).get_json()
    dias = {d["fecha"]: d for d in cuerpo["dias"]}
    assert (dias["2026-11-16"]["estado"], dias["2026-11-16"]["calorias_aprox"]) == ("cumplido", 50)
    assert (dias["2026-11-23"]["estado"], dias["2026-11-23"]["calorias_aprox"]) == ("incumplido", None)
    assert dias["2026-11-17"]["calorias_aprox"] is None  # descanso
    assert (dias["2026-11-30"]["estado"], dias["2026-11-30"]["calorias_aprox"]) == ("pendiente", None)
    assert cuerpo["calorias_nota"] == NOTA


# ---- Ninguna respuesta existente pierde campos ----------------------------------------------------

def test_ninguna_respuesta_pierde_campos(client, token):
    _perfil(client, token)
    lista = _lista(client, token)
    assert {"ejercicios", "total"} <= set(lista)
    assert {"id", "nombre", "grupo_muscular", "musculos_secundarios", "equipo", "nivel", "musculo_principal",
            "ambientes", "mecanica", "imagen_miniatura"} <= set(lista["ejercicios"][0])
    paginada = _lista(client, token, limit=2)
    assert {"ejercicios", "total", "items", "limit", "offset"} <= set(paginada)

    detalle = _detalle(client, token, "Press de banca con barra")
    assert {"nivel", "unidad", "reps_min", "reps_max", "series_min", "series_max", "descanso_seg", "rir",
            "dias_semana", "rpe", "peso_kg", "nota", "aviso"} <= set(detalle["recomendacion"])
    assert "recomendacion_motivo" in detalle

    agregado = _agregar(client, token, "Press de banca con barra")
    assert {"item", "rutina_copiada", "avisos"} <= set(agregado)
    assert {"item_id", "ejercicio_id", "nombre", "musculo_principal", "imagen_miniatura", "series", "repeticiones",
            "unidad", "peso_kg", "descanso_seg"} <= set(agregado["item"])

    plan = client.get("/api/plan/", headers=cabeceras(token)).get_json()
    assert {"dia_semana", "nombre_dia", "rutina", "ejercicios"} <= set(plan["plan"][0])

    sesion = client.post("/api/plan/completar", headers=cabeceras(token)).get_json()
    assert {"message", "sesion"} <= set(sesion)
    assert {"fecha", "dia_semana", "nombre_dia", "rutina", "completada_en"} <= set(sesion["sesion"])

    calendario = client.get("/api/calendario/?mes=2026-11", headers=cabeceras(token)).get_json()
    assert {"mes", "dias", "racha"} <= set(calendario)
    assert {"fecha", "dia_semana", "estado", "rutina"} <= set(calendario["dias"][0])
