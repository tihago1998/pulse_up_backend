"""Recomendación personalizada: cálculo puro, datos ausentes, contrato de la API y semillas."""
import sqlite3
from datetime import date

import pytest

from pulseup import inicializar_base_de_datos
from pulseup.core.semillas import ratios_por_nivel_app, sembrar_recomendaciones
from pulseup.modules.recomendaciones import repository as repo
from pulseup.modules.recomendaciones import service as rec
from tests.helpers import cabeceras, usuario_con_token

URL = "/api/ejercicios/"
HOY = date(2026, 11, 16)
NOTA_BRAZOS = (
    "Usa un peso que puedas controlar y con el que cumplas todas las repeticiones. Si no llegas al mínimo "
    "del rango, baja el peso; si llegas al máximo con facilidad, súbelo poco a poco."
)


# ---- Funciones puras --------------------------------------------------------------------

def test_epley():
    assert rec.peso_epley(100, 10) == pytest.approx(75.0)
    assert rec.peso_epley(130, 9) == pytest.approx(100.0)
    assert rec.peso_epley(80, 0) == 80


@pytest.mark.parametrize("rango, esperado", [((8, 12), 10), ((6, 12), 9), ((5, 10), 8), ((10, 15), 13), ((3, 5), 4)])
def test_reps_objetivo_es_el_punto_medio_redondeado(rango, esperado):
    assert rec.reps_objetivo(*rango) == esperado


@pytest.mark.parametrize("rango, esperado", [((8, 12), 12), ((6, 12), 11), ((5, 10), 10)])
def test_reps_para_epley_dejan_2_en_reserva(rango, esperado):
    assert rec.reps_para_epley(*rango) == esperado


@pytest.mark.parametrize("kg, esperado", [(77.0, 75.0), (74.99, 72.5), (75.0, 75.0), (2.6, 2.5), (2.4, 0.0), (0.3 * 25, 7.5)])
def test_redondeo_hacia_abajo_a_2_5(kg, esperado):
    assert rec.redondear_abajo(kg) == esperado


@pytest.mark.parametrize("edad, factor", [(14, 0.80), (17, 0.80), (18, 1.0), (35, 1.0), (50, 1.0), (51, 0.85), (90, 0.85)])
def test_ajuste_por_edad(edad, factor):
    assert rec.factor_edad(edad) == factor


def test_peso_con_ajuste_por_edad():
    # 1.25 × 80 = 100 kg de 1RM; 9 repeticiones → 76.9 kg
    assert rec.calcular_peso_kg(1.25, 80, 9, 25) == 75.0
    assert rec.calcular_peso_kg(1.25, 80, 9, 17) == 60.0  # 61.5 → 60
    assert rec.calcular_peso_kg(1.25, 80, 9, 51) == 65.0  # 65.4 → 65


def test_tope_de_peso_corporal_113_kg():
    assert rec.calcular_peso_kg(1.0, 150, 10, 30) == rec.calcular_peso_kg(1.0, 113, 10, 30) == 82.5
    assert rec.calcular_peso_kg(1.0, 112, 10, 30) == 82.5  # 84.0
    assert rec.calcular_peso_kg(1.0, 100, 10, 30) == 75.0


def test_peso_minimo_2_5_kg():
    assert rec.calcular_peso_kg(0.01, 30, 10, 16) == 2.5


@pytest.mark.parametrize("sexo, columna", [("hombre", "hombre"), ("mujer", "mujer"), ("no_indica", "mujer"),
                                           (None, "mujer"), ("otro", "mujer")])
def test_sexo_no_definido_usa_la_columna_de_mujer(sexo, columna):
    assert rec.sexo_para_ratio(sexo) == columna


def test_principiante_es_el_promedio_de_beginner_y_novice():
    fila = {"clave": "press_banca", "sexo": "hombre", "beginner": 0.5, "novice": 1.0, "intermediate": 1.25,
            "advanced": 1.5}
    assert ratios_por_nivel_app(fila) == {"principiante": 0.75, "intermedio": 1.25, "avanzado": 1.5}
    mujer = {"clave": "press_militar", "sexo": "mujer", "beginner": 0.2, "novice": 0.35, "intermediate": 0.5,
             "advanced": 0.7}
    assert ratios_por_nivel_app(mujer)["principiante"] == 0.275


def test_prensa_trae_los_niveles_de_la_app_tal_cual():
    fila = {"clave": "prensa", "sexo": "todos", "principiante": 1.2, "intermedio": 2.0, "avanzado": 3.0}
    assert ratios_por_nivel_app(fila) == {"principiante": 1.2, "intermedio": 2.0, "avanzado": 3.0}


def test_override_solo_cambia_series_y_repeticiones():
    regla = {"reps_min": 10, "reps_max": 20, "series_min": 3, "series_max": 4, "descanso_seg": 75, "nota": None}
    override = {"intermedio": {"reps_min": 5, "reps_max": 10, "series_min": 3, "series_max": 4, "descanso_seg": 1}}
    assert rec.aplicar_override(regla, override, "intermedio") == {**regla, "reps_min": 5, "reps_max": 10}
    assert rec.aplicar_override(regla, override, "avanzado") == regla
    assert rec.aplicar_override(regla, None, "intermedio") == regla


@pytest.mark.parametrize("valor", [None, "", "1998-02-30", "hoy"])
def test_edad_con_fecha_ausente_o_invalida_es_none(valor):
    assert rec.edad_de(valor, HOY) is None


# ---- Servicio con datos ausentes (código defensivo) ----------------------------------------

@pytest.fixture
def conn(app, db_path):
    conexion = sqlite3.connect(db_path)
    conexion.row_factory = sqlite3.Row
    yield conexion
    conexion.close()


def _ejercicio(conn, nombre):
    return conn.execute("SELECT * FROM ejercicio WHERE nombre = ?", (nombre,)).fetchone()


PERFIL = {"nivel": "intermedio", "peso_kg": 80.0, "sexo": "hombre", "fecha_nacimiento": "2001-03-10"}


def test_prensa_no_depende_del_sexo(conn):
    assert repo.ratio(conn, "prensa", "hombre", "intermedio") == repo.ratio(conn, "prensa", "mujer", "intermedio") == 2.0


@pytest.mark.parametrize("falta", ["peso_kg", "fecha_nacimiento"])
def test_perfil_sin_peso_o_sin_edad_da_reglas_sin_peso(conn, falta):
    perfil = {k: v for k, v in PERFIL.items() if k != falta}
    recomendacion, motivo = rec.recomendacion_para(conn, _ejercicio(conn, "Press de banca con barra"), perfil, HOY)
    assert motivo is None
    assert (recomendacion["reps_min"], recomendacion["reps_max"], recomendacion["peso_kg"]) == (6, 12, None)
    assert recomendacion["nota"] == rec.NOTA_SIN_PESO


def test_perfil_sin_sexo_usa_la_columna_de_mujer(conn):
    banca = _ejercicio(conn, "Press de banca con barra")
    sin_sexo = {k: v for k, v in PERFIL.items() if k != "sexo"}
    mujer = {**PERFIL, "sexo": "mujer"}
    # Intermedio: 6-12 → 9 + 2 = 11 repeticiones para Epley
    assert rec.recomendacion_para(conn, banca, sin_sexo, HOY)[0]["peso_kg"] == 42.5  # 0.75 × 80 / (1 + 11/30)
    assert rec.recomendacion_para(conn, banca, mujer, HOY)[0]["peso_kg"] == 42.5
    assert rec.recomendacion_para(conn, banca, PERFIL, HOY)[0]["peso_kg"] == 72.5  # 1.25 × 80 / (1 + 11/30)


@pytest.mark.parametrize("perfil", [None, {}, {**PERFIL, "nivel": None}, {**PERFIL, "nivel": "experto"}])
def test_perfil_sin_nivel_no_da_recomendacion(conn, perfil):
    assert rec.recomendacion_para(conn, _ejercicio(conn, "Flexiones"), perfil, HOY) == (None, rec.MOTIVO_SIN_PERFIL)


def test_ejercicio_sin_tipo_no_da_recomendacion(conn):
    fila = dict(_ejercicio(conn, "Flexiones"))
    fila["tipo_recomendacion"] = None
    assert rec.recomendacion_para(conn, fila, PERFIL, HOY) == (None, rec.MOTIVO_SIN_REGLA)


# ---- Contrato de la API -----------------------------------------------------------------------

@pytest.fixture
def token(client, fijar_hoy):
    fijar_hoy(HOY)
    return usuario_con_token(client)[1]


def _perfil(client, token, **cambios):
    cuerpo = {"fecha_nacimiento": "2001-03-10", "sexo": "hombre", "peso_kg": 80, "estatura_cm": 178,
              "nivel": "intermedio", **cambios}
    r = client.put("/api/perfil-fisico/", json=cuerpo, headers=cabeceras(token))
    assert r.status_code == 200, r.get_json()


def _id(client, token, nombre):
    ejercicios = client.get(URL, query_string={"q": nombre}, headers=cabeceras(token)).get_json()["ejercicios"]
    return next(e["id"] for e in ejercicios if e["nombre"] == nombre)


def _rec(client, token, nombre):
    """Recomendación del detalle; comprueba que el endpoint dedicado responda lo mismo."""
    id_ejercicio = _id(client, token, nombre)
    detalle = client.get(f"{URL}{id_ejercicio}", headers=cabeceras(token)).get_json()["ejercicio"]
    propia = client.get(f"{URL}{id_ejercicio}/recomendacion", headers=cabeceras(token)).get_json()
    assert propia == {"recomendacion": detalle["recomendacion"], "recomendacion_motivo": detalle["recomendacion_motivo"]}
    return detalle["recomendacion"], detalle["recomendacion_motivo"]


def _esperada(**campos):
    base = {"nivel": "intermedio", "unidad": "repeticiones", "descanso_seg": None, "rir": None, "dias_semana": None,
            "rpe": None, "peso_kg": None, "nota": None, "aviso": rec.AVISO}
    return {**base, **campos}


def test_sin_perfil_recomendacion_null_con_motivo(client, token):
    assert _rec(client, token, "Press de banca con barra") == (None, "Completa tu perfil físico para ver la recomendación")


def test_carga_compuesto_con_referencia(client, token):
    _perfil(client, token)
    recomendacion, motivo = _rec(client, token, "Press de banca con barra")
    assert motivo is None
    assert recomendacion == _esperada(reps_min=6, reps_max=12, series_min=3, series_max=4, descanso_seg=150, rir="2-3",
                                      peso_kg=72.5)


@pytest.mark.parametrize("nivel, banca, sentadilla, prensa", [("intermedio", 72.5, 100.0, 115.0),
                                                              ("principiante", 42.5, 55.0, 67.5)])
def test_tabla_de_ejemplo_hombre_80_kg_25_anos(client, token, nivel, banca, sentadilla, prensa):
    _perfil(client, token, nivel=nivel)
    pesos = [_rec(client, token, n)[0]["peso_kg"] for n in ("Press de banca con barra", "Sentadilla con barra",
                                                           "Prensa de piernas")]
    assert pesos == [banca, sentadilla, prensa]


@pytest.mark.parametrize("nacimiento, peso", [("2009-11-17", 57.5), ("2008-11-16", 72.5), ("1976-11-16", 72.5),
                                              ("1975-11-16", 60.0)])
def test_ajuste_por_edad_en_la_api(client, token, nacimiento, peso):
    # 2009-11-17 → 16 años; 2008-11-16 → 18; 1976-11-16 → 50; 1975-11-16 → 51. Base 73.2 kg (× 0.80 / × 0.85)
    _perfil(client, token, fecha_nacimiento=nacimiento)
    assert _rec(client, token, "Press de banca con barra")[0]["peso_kg"] == peso


def test_sexo_no_indica_usa_la_columna_de_mujer(client, token):
    _perfil(client, token, sexo="no_indica")
    assert _rec(client, token, "Press de banca con barra")[0]["peso_kg"] == 42.5


def test_carga_compuesto_sin_referencia(client, token):
    _perfil(client, token)
    recomendacion, _ = _rec(client, token, "Press de pecho con mancuernas")
    assert recomendacion == _esperada(reps_min=6, reps_max=12, series_min=3, series_max=4, descanso_seg=150, rir="2-3",
                                      nota=rec.NOTA_SIN_PESO)


def test_peso_muerto_rumano_no_tiene_referencia(client, token):
    _perfil(client, token)
    recomendacion, _ = _rec(client, token, "Peso muerto rumano")
    assert recomendacion == _esperada(reps_min=6, reps_max=12, series_min=3, series_max=4, descanso_seg=150, rir="2-3",
                                      nota=rec.NOTA_SIN_PESO)


def test_carga_aislamiento(client, token):
    _perfil(client, token)
    recomendacion, _ = _rec(client, token, "Elevaciones laterales")
    assert recomendacion == _esperada(reps_min=8, reps_max=15, series_min=3, series_max=4, descanso_seg=75, rir="0-2",
                                      nota=rec.NOTA_SIN_PESO)


def test_carga_brazos_mantiene_su_nota(client, token):
    _perfil(client, token)
    recomendacion, _ = _rec(client, token, "Curl martillo")
    assert recomendacion == _esperada(reps_min=8, reps_max=15, series_min=3, series_max=4, descanso_seg=75,
                                      nota=NOTA_BRAZOS)


def test_peso_corporal(client, token):
    _perfil(client, token)
    recomendacion, _ = _rec(client, token, "Flexiones")
    assert recomendacion == _esperada(reps_min=10, reps_max=20, series_min=3, series_max=4, descanso_seg=75)


def test_peso_corporal_avanzado_sugiere_variante(client, token):
    _perfil(client, token, nivel="avanzado")
    recomendacion, _ = _rec(client, token, "Sentadilla")
    assert (recomendacion["reps_min"], recomendacion["reps_max"]) == (20, 25)
    assert "variante más difícil" in recomendacion["nota"]


@pytest.mark.parametrize("nivel, reps, series", [("principiante", (3, 5), (3, 3)), ("intermedio", (5, 10), (3, 4)),
                                                 ("avanzado", (10, 15), (3, 4))])
def test_dominadas_con_override(client, token, nivel, reps, series):
    _perfil(client, token, nivel=nivel)
    recomendacion, _ = _rec(client, token, "Dominadas")
    assert (recomendacion["reps_min"], recomendacion["reps_max"]) == reps
    assert (recomendacion["series_min"], recomendacion["series_max"]) == series
    assert recomendacion["peso_kg"] is None


def test_abdomen(client, token):
    _perfil(client, token)
    recomendacion, _ = _rec(client, token, "Abdominales crunch")
    assert recomendacion == _esperada(reps_min=15, reps_max=20, series_min=3, series_max=4, descanso_seg=60)


def test_isometrico_en_segundos(client, token):
    _perfil(client, token, nivel="principiante")
    recomendacion, _ = _rec(client, token, "Plancha")
    assert recomendacion == _esperada(nivel="principiante", unidad="segundos", reps_min=20, reps_max=30, series_min=2,
                                      series_max=3, descanso_seg=45)


def test_cardio_en_minutos(client, token):
    _perfil(client, token)
    recomendacion, _ = _rec(client, token, "Bicicleta estática")
    nota = recomendacion.pop("nota")
    assert recomendacion == {k: v for k, v in _esperada(
        unidad="minutos", reps_min=30, reps_max=40, series_min=1, series_max=1, dias_semana="3-4", rpe="5-6").items()
        if k != "nota"}
    assert "1-2 días por semana, 2-3 rondas" in nota and "OMS: 150-300 minutos" in nota


def test_endpoint_de_recomendacion_404_y_401(client, token):
    assert client.get(f"{URL}99999/recomendacion", headers=cabeceras(token)).status_code == 404
    assert client.get(f"{URL}1/recomendacion").status_code == 401


def test_lista_y_rutinas_no_cambian(client, token):
    _perfil(client, token)
    item = client.get(URL, headers=cabeceras(token)).get_json()["ejercicios"][0]
    assert "recomendacion" not in item and "recomendacion_motivo" not in item
    rutina = client.get("/api/rutinas/", headers=cabeceras(token)).get_json()["rutinas"][0]
    detalle = client.get(f"/api/rutinas/{rutina['id']}", headers=cabeceras(token)).get_json()["rutina"]
    assert "recomendacion" not in detalle["ejercicios"][0]["ejercicio"]


# ---- Semillas ---------------------------------------------------------------------------------

def test_semillas_de_recomendacion_idempotentes(app, db_path, conn):
    conteos = lambda: (conn.execute("SELECT COUNT(*) FROM recomendacion_regla").fetchone()[0],  # noqa: E731
                       conn.execute("SELECT COUNT(*) FROM referencia_fuerza_ratio").fetchone()[0])
    assert conteos() == (21, 39)
    inicializar_base_de_datos(db_path)
    inicializar_base_de_datos(db_path)
    assert conteos() == (21, 39)


def test_las_semillas_reaplican_los_valores_del_json(conn):
    conn.execute("UPDATE recomendacion_regla SET reps_min = 99 WHERE tipo = 'abdomen' AND nivel = 'avanzado'")
    conn.execute("UPDATE referencia_fuerza_ratio SET ratio = 9 WHERE clave = 'prensa'")
    sembrar_recomendaciones(conn)
    assert repo.regla(conn, "abdomen", "avanzado")["reps_min"] == 20
    assert repo.ratio(conn, "prensa", "mujer", "avanzado") == 3.0


def test_referencia_solo_en_las_variantes_exactas(conn):
    filas = conn.execute("SELECT nombre, referencia_fuerza FROM ejercicio WHERE referencia_fuerza IS NOT NULL").fetchall()
    assert dict(filas) == {
        "Press de banca con barra": "press_banca",
        "Sentadilla con barra": "sentadilla",
        "Peso muerto con barra": "peso_muerto",
        "Press militar de pie con barra": "press_militar",
        "Remo con barra": "remo_barra",
        "Jalón al pecho": "jalon_pecho",
        "Prensa de piernas": "prensa",
    }
    overrides = conn.execute("SELECT nombre FROM ejercicio WHERE recomendacion_override IS NOT NULL").fetchall()
    assert [f["nombre"] for f in overrides] == ["Dominadas"]
