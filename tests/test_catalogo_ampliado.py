"""Catálogo ampliado: selección curada, fotos, filtros, paginación, detalle y créditos."""
import json
import shutil
import sqlite3
import uuid
from pathlib import Path

import pytest

from pulseup import inicializar_base_de_datos
from pulseup.core.esquema import crear_esquema
from pulseup.core.semillas import sembrar_catalogo, sembrar_ejercicios_base, sembrar_rutinas
from pulseup.modules.recomendaciones.service import MOTIVO_SIN_PERFIL
from tests.helpers import cabeceras, usuario_con_token
from tools import importar_catalogo

URL = "/api/ejercicios/"
TOTAL_CATALOGO = 150
CON_FOTOS = 142
SEMILLA = json.loads(Path(importar_catalogo.SEMILLA).read_text(encoding="utf-8"))
BASE = json.loads((Path(importar_catalogo.SEMILLA).parent / "ejercicios.json").read_text(encoding="utf-8"))


def _jpeg_falso(url, archivo):
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_bytes(b"\xff\xd8\xff" + url.encode())


def _importar(db_path, destino, descargar=_jpeg_falso):
    return importar_catalogo.importar(db_path, destino=destino, descargar=descargar, salida=lambda *_: None)


def _contar(db_path, tabla):
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    finally:
        conn.close()


@pytest.fixture
def h(client):
    return cabeceras(usuario_con_token(client)[1])


@pytest.fixture
def con_fotos(app, db_path, tmp_path):
    """Importa las fotos del catálogo con un descargador falso (sin red)."""
    return _importar(db_path, tmp_path / "fotos")


def _por_nombre(client, h, nombre):
    ejercicios = client.get(URL, query_string={"q": nombre}, headers=h).get_json()["ejercicios"]
    return next(e for e in ejercicios if e["nombre"] == nombre)


# ---- Semilla e importador -----------------------------------------------------------

def test_la_seleccion_tiene_150_y_cubre_ambientes_y_musculos():
    assert len(SEMILLA) == TOTAL_CATALOGO
    assert len({e["nombre"] for e in SEMILLA}) == TOTAL_CATALOGO
    assert {a for e in SEMILLA for a in e["ambientes"]} == {"gimnasio", "casa", "calistenia"}
    musculos = {e["musculo_principal"] for e in SEMILLA}
    assert {"pecho", "espalda", "cuadriceps", "hombros", "biceps", "triceps", "abdomen",
            "pantorrillas", "gluteos", "cardio"} <= musculos
    for e in SEMILLA:
        assert len(e["pasos"]) >= 3 and 2 <= len(e["errores_comunes"]) <= 3, e["nombre"]
        assert e["respiracion"] and e["variante_facil"] and e["variante_dificil"], e["nombre"]


def test_sembrar_e_importar_dos_veces_no_duplica(app, db_path, tmp_path):
    primera = _importar(db_path, tmp_path / "fotos")
    conteos = (_contar(db_path, "ejercicio"), _contar(db_path, "ejercicio_imagen"))
    inicializar_base_de_datos(db_path)
    segunda = _importar(db_path, tmp_path / "fotos")
    assert conteos == (TOTAL_CATALOGO, CON_FOTOS * 2)
    assert (_contar(db_path, "ejercicio"), _contar(db_path, "ejercicio_imagen")) == conteos
    assert (primera["descargadas"], segunda["descargadas"], segunda["ya_estaban"]) == (CON_FOTOS * 2, 0, CON_FOTOS * 2)


def test_una_foto_que_falla_se_anota_y_se_sigue(app, db_path, tmp_path):
    def descargar(url, archivo):
        if "/Pushups/1.jpg" in url:
            raise OSError("HTTP 404")
        _jpeg_falso(url, archivo)

    resumen = _importar(db_path, tmp_path / "fotos", descargar)
    assert resumen["fallos"] == [("Pushups", 1, "HTTP 404")]
    assert _contar(db_path, "ejercicio_imagen") == CON_FOTOS * 2 - 1
    assert "Pushups\t1\tHTTP 404" in (tmp_path / "fotos" / "errores_importacion.log").read_text(encoding="utf-8")


def _ids_por_nombre(conn):
    return {n: i for i, n in conn.execute("SELECT id, nombre FROM ejercicio").fetchall()}


def test_los_ejercicios_existentes_conservan_su_id(tmp_path):
    """Base de datos creada con el esquema y las semillas de antes: al ampliar no cambian los ids."""
    db = str(tmp_path / "antigua.db")
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE ejercicio (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE,
           grupo_muscular TEXT NOT NULL, musculos_secundarios TEXT NOT NULL DEFAULT '[]',
           equipo TEXT NOT NULL, nivel TEXT NOT NULL, instrucciones TEXT NOT NULL DEFAULT '[]')"""
    )
    # Ids a propósito no consecutivos, como en una base que ya tuvo altas y bajas
    for posicion, e in enumerate(BASE):
        conn.execute(
            "INSERT INTO ejercicio (id, nombre, grupo_muscular, equipo, nivel) VALUES (?, ?, ?, ?, ?)",
            (1000 - posicion * 3, e["nombre"], e["grupo_muscular"], e["equipo"], e["nivel"]),
        )
    crear_esquema(conn)
    sembrar_rutinas(conn)
    antes = _ids_por_nombre(conn)
    rutinas_antes = conn.execute("SELECT id_rutina, id_ejercicio FROM rutina_ejercicio ORDER BY id").fetchall()

    sembrar_catalogo(conn)
    sembrar_catalogo(conn)
    despues = _ids_por_nombre(conn)
    assert len(despues) == TOTAL_CATALOGO
    assert {n: despues[n] for n in antes} == antes
    assert conn.execute("SELECT id_rutina, id_ejercicio FROM rutina_ejercicio ORDER BY id").fetchall() == rutinas_antes
    flexiones = conn.execute("SELECT * FROM ejercicio WHERE nombre = 'Flexiones'").fetchone()
    assert flexiones["id_externo"] == "Pushups"
    assert flexiones["grupo_muscular"] == "pecho"
    assert json.loads(flexiones["ambientes"]) == ["casa", "calistenia"]
    conn.close()


def test_las_semillas_base_y_ampliadas_no_se_pisan(tmp_path):
    """sembrar_ejercicios_base después del ampliado (reinicio) no deshace la actualización."""
    db = str(tmp_path / "pulseup.db")
    inicializar_base_de_datos(db)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    sembrar_ejercicios_base(conn)
    plancha = conn.execute("SELECT pasos, instrucciones FROM ejercicio WHERE nombre = 'Plancha'").fetchone()
    assert json.loads(plancha["pasos"]) == json.loads(plancha["instrucciones"])
    assert len(json.loads(plancha["pasos"])) == 4
    conn.close()


# ---- Listado, filtros y paginación --------------------------------------------------

def test_listado_sin_paginar_mantiene_la_forma_actual(client, h):
    cuerpo = client.get(URL, headers=h).get_json()
    assert set(cuerpo) == {"ejercicios", "total"}
    assert cuerpo["total"] == len(cuerpo["ejercicios"]) == TOTAL_CATALOGO
    primero = cuerpo["ejercicios"][0]
    viejos = {"id", "nombre", "grupo_muscular", "musculos_secundarios", "equipo", "nivel"}
    nuevos = {"musculo_principal", "ambientes", "mecanica", "imagen_miniatura"}
    assert set(primero) == viejos | nuevos
    assert "instrucciones" not in primero


def test_paginacion(client, h):
    cuerpo = client.get(URL, query_string={"limit": 2}, headers=h).get_json()
    assert (cuerpo["total"], cuerpo["limit"], cuerpo["offset"], len(cuerpo["items"])) == (TOTAL_CATALOGO, 2, 0, 2)
    assert cuerpo["items"] == cuerpo["ejercicios"]
    todos = [e["id"] for e in client.get(URL, headers=h).get_json()["ejercicios"]]
    pagina = client.get(URL, query_string={"limit": 3, "offset": 4}, headers=h).get_json()["items"]
    assert [e["id"] for e in pagina] == todos[4:7]
    final = client.get(URL, query_string={"offset": TOTAL_CATALOGO - 2, "limit": 10}, headers=h).get_json()
    assert len(final["items"]) == 2
    assert client.get(URL, query_string={"formato": "paginado"}, headers=h).get_json()["limit"] == 20
    assert client.get(URL, query_string={"limit": 500}, headers=h).get_json()["limit"] == 100


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": "diez"}, {"offset": -1}, {"offset": "x"}])
def test_paginacion_invalida(client, h, params):
    r = client.get(URL, query_string=params, headers=h)
    assert r.status_code == 400
    assert "error" in r.get_json()


def test_filtrar_por_ambiente(client, h):
    for ambiente in ("gimnasio", "casa", "calistenia"):
        cuerpo = client.get(URL, query_string={"ambiente": ambiente}, headers=h).get_json()
        esperados = sum(1 for e in SEMILLA if ambiente in e["ambientes"])
        assert cuerpo["total"] == len(cuerpo["ejercicios"]) == esperados
        assert all(ambiente in e["ambientes"] for e in cuerpo["ejercicios"])
    assert client.get(URL, query_string={"ambiente": "playa"}, headers=h).status_code == 400


def test_filtros_combinados_con_paginacion(client, h):
    params = {"ambiente": "gimnasio", "equipo": "polea", "musculo": "triceps", "limit": 1}
    cuerpo = client.get(URL, query_string=params, headers=h).get_json()
    esperados = [e for e in SEMILLA if e["equipo"] == "polea" and e["musculo_principal"] == "triceps"]
    assert cuerpo["total"] == len(esperados) > 1
    assert len(cuerpo["items"]) == 1
    nombres = client.get(URL, query_string={"q": "dominadas", "nivel": "principiante"}, headers=h).get_json()
    assert [e["nombre"] for e in nombres["ejercicios"]] == ["Dominadas asistidas con banda"]


def test_filtros_disponibles_incluyen_ambientes(client, h):
    datos = client.get(URL + "filtros", headers=h).get_json()
    assert datos["ambientes"] == ["gimnasio", "casa", "calistenia"]
    assert "pecho" in datos["musculos"] and "polea" in datos["equipos"]
    assert datos["niveles"] == ["principiante", "intermedio", "avanzado"]


# ---- Detalle, fotos y recomendación ---------------------------------------------------

def test_detalle_con_dos_fotos_ordenadas(client, h, con_fotos):
    item = _por_nombre(client, h, "Press de banca con barra")
    base = "/static/ejercicios/Barbell_Bench_Press_-_Medium_Grip"
    assert item["imagen_miniatura"] == f"{base}/0.jpg"
    detalle = client.get(f"{URL}{item['id']}", headers=h).get_json()["ejercicio"]
    assert detalle["imagenes"] == [{"orden": 0, "url": f"{base}/0.jpg"}, {"orden": 1, "url": f"{base}/1.jpg"}]
    assert detalle["imagen_miniatura"] == f"{base}/0.jpg"
    assert detalle["musculo_principal"] == "pecho" and detalle["ambientes"] == ["gimnasio"]
    assert detalle["pasos"] == detalle["instrucciones"] and len(detalle["pasos"]) == 5
    assert len(detalle["errores_comunes"]) == 3
    assert detalle["respiracion"] and detalle["variante_facil"] and detalle["variante_dificil"]
    assert detalle["descanso_seg"] == 120


def test_ejercicio_sin_equivalente_no_tiene_fotos(client, h, con_fotos):
    item = _por_nombre(client, h, "Burpees")
    assert item["imagen_miniatura"] is None
    detalle = client.get(f"{URL}{item['id']}", headers=h).get_json()["ejercicio"]
    assert detalle["imagenes"] == [] and detalle["imagen_miniatura"] is None


def test_recomendacion_sin_perfil_fisico(client, h):
    item = _por_nombre(client, h, "Press de banca con barra")
    detalle = client.get(f"{URL}{item['id']}", headers=h).get_json()["ejercicio"]
    assert detalle["recomendacion"] is None
    assert detalle["recomendacion_motivo"] == MOTIVO_SIN_PERFIL == "Completa tu perfil físico para ver la recomendación"


# Antes del módulo de recomendaciones esto devolvía null; el detalle de cada tipo se prueba en
# test_recomendaciones.py
@pytest.mark.parametrize("nombre", ["Press de banca con barra", "Flexiones", "Plancha", "Curl martillo"])
def test_recomendacion_con_perfil_ya_se_calcula(client, h, nombre):
    perfil = {"fecha_nacimiento": "1998-03-10", "sexo": "hombre", "peso_kg": 72.5, "estatura_cm": 175,
              "nivel": "intermedio"}
    assert client.put("/api/perfil-fisico/", json=perfil, headers=h).status_code == 200
    item = _por_nombre(client, h, nombre)
    detalle = client.get(f"{URL}{item['id']}", headers=h).get_json()["ejercicio"]
    assert detalle["recomendacion"]["nivel"] == "intermedio"
    assert detalle["recomendacion_motivo"] is None


# ---- Créditos y archivos estáticos ----------------------------------------------------

def test_creditos(client, h, con_fotos):
    datos = client.get(URL + "creditos", headers=h).get_json()
    assert datos["creditos"] == [
        {
            "fuente": "free-exercise-db",
            "licencia": "Unlicense (repositorio); origen de las fotos no documentado",
            "autor": None,
            "atribucion": importar_catalogo.ATRIBUCION,
            "imagenes": CON_FOTOS * 2,
        }
    ]


def test_creditos_sin_fotos_importadas(client, h):
    assert client.get(URL + "creditos", headers=h).get_json()["creditos"] == []


@pytest.mark.parametrize("ruta", ["", "filtros", "creditos", "1"])
def test_endpoints_requieren_token(client, ruta):
    assert client.get(URL + ruta).status_code == 401


def test_flask_sirve_las_fotos_en_static(app, client):
    carpeta = Path(app.static_folder) / "ejercicios" / f"_prueba_{uuid.uuid4().hex}"
    carpeta.mkdir(parents=True)
    try:
        (carpeta / "0.jpg").write_bytes(b"\xff\xd8\xffprueba")
        r = client.get(f"/static/ejercicios/{carpeta.name}/0.jpg")
        assert r.status_code == 200
        assert r.data == b"\xff\xd8\xffprueba"
        r.close()
    finally:
        shutil.rmtree(carpeta)
