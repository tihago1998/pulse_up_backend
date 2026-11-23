"""Perfil físico: guardar, ver y borrar los datos del usuario, con la edad calculada en el servidor."""
import sqlite3
from datetime import date

import pytest

from pulseup.core.roles import ID_SUPERADMINISTRADOR
from tests.helpers import cabeceras, usuario_con_rol, usuario_con_token

URL = "/api/perfil-fisico/"
# 16 de noviembre de 2026 (lunes)
HOY = date(2026, 11, 16)

VALIDO = {
    "fecha_nacimiento": "1998-03-10",
    "sexo": "hombre",
    "peso_kg": 72.5,
    "estatura_cm": 175,
    "nivel": "intermedio",
}


@pytest.fixture
def ana(client, fijar_hoy):
    """Token de un usuario recién registrado, con "hoy" fijado en HOY."""
    fijar_hoy(HOY)
    return usuario_con_token(client)[1]


def _put(client, token, cuerpo):
    return client.put(URL, json=cuerpo, headers=cabeceras(token))


def _get(client, token):
    r = client.get(URL, headers=cabeceras(token))
    assert r.status_code == 200
    return r.get_json()["perfil"]


def _error(client, token, **cambios):
    """Envía VALIDO con `cambios` (None = quitar el campo) y devuelve el mensaje del 400."""
    cuerpo = {**VALIDO, **cambios}
    cuerpo = {k: v for k, v in cuerpo.items() if v is not None}
    r = _put(client, token, cuerpo)
    assert r.status_code == 400, r.get_json()
    return r.get_json()["error"]


# ---- Autenticación ------------------------------------------------------------------

@pytest.mark.parametrize("metodo", ["get", "put", "delete"])
def test_sin_token_responde_401(client, metodo):
    r = getattr(client, metodo)(URL, json=VALIDO)
    assert r.status_code == 401


# ---- Guardar y ver ------------------------------------------------------------------

def test_sin_perfil_devuelve_null(client, ana):
    r = client.get(URL, headers=cabeceras(ana))
    assert r.status_code == 200
    assert r.get_json() == {"perfil": None}


def test_guardar_y_ver(client, ana):
    r = _put(client, ana, VALIDO)
    assert r.status_code == 200
    cuerpo = r.get_json()
    assert cuerpo["message"] == "Perfil guardado"
    esperado = {
        "fecha_nacimiento": "1998-03-10",
        "edad": 28,  # cumplió años en marzo
        "sexo": "hombre",
        "peso_kg": 72.5,
        "estatura_cm": 175.0,
        "nivel": "intermedio",
        "actualizado_en": "2026-11-16T18:30:00-05:00",
    }
    assert cuerpo["perfil"] == esperado
    assert _get(client, ana) == esperado


def test_edad_antes_del_cumpleanos_del_ano(client, ana):
    _put(client, ana, {**VALIDO, "fecha_nacimiento": "1998-12-01"})
    assert _get(client, ana)["edad"] == 27


def test_edad_el_dia_del_cumpleanos(client, ana):
    _put(client, ana, {**VALIDO, "fecha_nacimiento": "1998-11-16"})
    assert _get(client, ana)["edad"] == 28


def test_la_edad_se_calcula_con_hoy_y_no_se_guarda(client, ana, fijar_hoy):
    _put(client, ana, {**VALIDO, "fecha_nacimiento": "1998-11-17"})
    assert _get(client, ana)["edad"] == 27
    fijar_hoy(date(2026, 11, 17))
    assert _get(client, ana)["edad"] == 28


def test_cumple_14_justo_hoy(client, ana):
    r = _put(client, ana, {**VALIDO, "fecha_nacimiento": "2012-11-16"})
    assert r.status_code == 200
    assert r.get_json()["perfil"]["edad"] == 14


def test_cumple_14_manana_aun_no_puede(client, ana):
    error = _error(client, ana, fecha_nacimiento="2012-11-17")
    assert error == "Debes tener al menos 14 años para usar PulseUp"


def test_edad_maxima_100(client, ana):
    assert _put(client, ana, {**VALIDO, "fecha_nacimiento": "1926-01-01"}).status_code == 200  # 100 años
    error = _error(client, ana, fecha_nacimiento="1925-11-15")  # 101 años
    assert "100" in error


def test_sexo_es_opcional(client, ana):
    sin_sexo = {k: v for k, v in VALIDO.items() if k != "sexo"}
    r = _put(client, ana, sin_sexo)
    assert r.status_code == 200
    assert r.get_json()["perfil"]["sexo"] == "no_indica"


@pytest.mark.parametrize("sexo", ["hombre", "mujer", "no_indica"])
def test_sexos_validos(client, ana, sexo):
    assert _put(client, ana, {**VALIDO, "sexo": sexo}).get_json()["perfil"]["sexo"] == sexo


def test_medidas_con_un_decimal_y_en_los_bordes(client, ana):
    perfil = _put(client, ana, {**VALIDO, "peso_kg": 70.26, "estatura_cm": 172.04}).get_json()["perfil"]
    assert (perfil["peso_kg"], perfil["estatura_cm"]) == (70.3, 172.0)
    for peso, estatura in ((30, 100), (300, 250)):
        perfil = _put(client, ana, {**VALIDO, "peso_kg": peso, "estatura_cm": estatura}).get_json()["perfil"]
        assert (perfil["peso_kg"], perfil["estatura_cm"]) == (float(peso), float(estatura))


def test_campos_desconocidos_se_ignoran(client, ana):
    r = _put(client, ana, {**VALIDO, "imc": 99, "id_usuario": 12345})
    assert r.status_code == 200
    assert "imc" not in r.get_json()["perfil"]


def test_guardar_dos_veces_reemplaza(client, ana, db_path, fijar_hoy):
    _put(client, ana, VALIDO)
    fijar_hoy(date(2026, 11, 20))
    r = _put(client, ana, {**VALIDO, "peso_kg": 70, "nivel": "avanzado", "sexo": "mujer"})
    assert r.status_code == 200
    perfil = _get(client, ana)
    assert (perfil["peso_kg"], perfil["nivel"], perfil["sexo"]) == (70.0, "avanzado", "mujer")
    assert perfil["actualizado_en"] == "2026-11-20T18:30:00-05:00"
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM perfil_fisico").fetchone()[0] == 1
    conn.close()


# ---- Validaciones -------------------------------------------------------------------

def test_fecha_futura(client, ana):
    assert _error(client, ana, fecha_nacimiento="2026-11-17") == "La fecha de nacimiento no puede ser futura"


@pytest.mark.parametrize("fecha", ["10/03/1998", "1998-3-10", "1998-02-30", "19980310", "hoy", "", 19980310])
def test_fecha_mal_formada(client, ana, fecha):
    assert _error(client, ana, fecha_nacimiento=fecha) == "Fecha de nacimiento inválida, usa el formato YYYY-MM-DD"


@pytest.mark.parametrize("peso", [29.9, 300.1, 0, -70])
def test_peso_fuera_de_rango(client, ana, peso):
    assert _error(client, ana, peso_kg=peso) == "peso_kg debe estar entre 30 y 300 kg"


@pytest.mark.parametrize("estatura", [99.9, 250.1])
def test_estatura_fuera_de_rango(client, ana, estatura):
    assert _error(client, ana, estatura_cm=estatura) == "estatura_cm debe estar entre 100 y 250 cm"


@pytest.mark.parametrize("valor", ["70", "setenta", True, False, [70], {"kg": 70}])
@pytest.mark.parametrize("campo", ["peso_kg", "estatura_cm"])
def test_medidas_que_no_son_numeros(client, ana, campo, valor):
    assert _error(client, ana, **{campo: valor}) == f"{campo} debe ser un número"


@pytest.mark.parametrize("nivel", ["experto", "", "Intermedio", 1])
def test_nivel_invalido(client, ana, nivel):
    assert _error(client, ana, nivel=nivel).startswith("Nivel no válido")


@pytest.mark.parametrize("sexo", ["otro", "", "Hombre", 1, True])
def test_sexo_invalido(client, ana, sexo):
    assert _error(client, ana, sexo=sexo).startswith("Sexo no válido")


@pytest.mark.parametrize("campo", ["fecha_nacimiento", "peso_kg", "estatura_cm", "nivel"])
def test_falta_un_campo_obligatorio(client, ana, campo):
    assert _error(client, ana, **{campo: None}) == f"Faltan campos obligatorios: {campo}"


def test_cuerpo_vacio(client, ana):
    for r in (_put(client, ana, {}), client.put(URL, headers=cabeceras(ana))):
        assert r.status_code == 400
        assert r.get_json()["error"] == "Faltan campos obligatorios: fecha_nacimiento, peso_kg, estatura_cm, nivel"


def test_cuerpo_que_no_es_objeto(client, ana):
    r = _put(client, ana, [VALIDO])
    assert r.status_code == 400
    assert r.get_json()["error"] == "El cuerpo debe ser un objeto JSON"


def test_un_error_no_cambia_el_perfil_guardado(client, ana):
    _put(client, ana, VALIDO)
    _error(client, ana, peso_kg=500)
    assert _get(client, ana)["peso_kg"] == 72.5


# ---- Aislamiento y borrado ----------------------------------------------------------

def test_cada_usuario_ve_solo_su_perfil(client, ana):
    _, beto = usuario_con_token(client, "Beto", "beto@test.com")
    _put(client, ana, VALIDO)
    assert _get(client, beto) is None
    _put(client, beto, {**VALIDO, "peso_kg": 90})
    assert _get(client, ana)["peso_kg"] == 72.5
    assert _get(client, beto)["peso_kg"] == 90.0


def test_eliminar_perfil(client, ana):
    _put(client, ana, VALIDO)
    r = client.delete(URL, headers=cabeceras(ana))
    assert r.status_code == 200
    assert r.get_json() == {"message": "Perfil eliminado"}
    assert _get(client, ana) is None
    # Borrar cuando ya no existe también responde 200
    assert client.delete(URL, headers=cabeceras(ana)).get_json() == {"message": "Perfil eliminado"}


def test_eliminar_usuario_borra_su_perfil(client, db_path, fijar_hoy):
    fijar_hoy(HOY)
    id_ana, token_ana = usuario_con_token(client)
    _put(client, token_ana, VALIDO)
    _, token_super = usuario_con_rol(client, db_path, [ID_SUPERADMINISTRADOR], "Super", "super@test.com")
    assert client.delete(f"/api/users/{id_ana}", headers=cabeceras(token_super)).status_code == 200
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM perfil_fisico WHERE id_usuario = ?", (id_ana,)).fetchone()[0] == 0
    conn.close()
