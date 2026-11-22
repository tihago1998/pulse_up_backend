"""Contrato de /api/auth: lo que la app Android espera de registro y login."""
from tests.helpers import registrar, iniciar_sesion


def test_registro_exitoso(client):
    r = registrar(client)
    assert r.status_code == 201
    cuerpo = r.get_json()
    assert cuerpo["message"] == "Usuario registrado"
    assert isinstance(cuerpo["id_usuario"], int)


def test_registro_con_campos_faltantes(client):
    r = client.post("/api/auth/register", json={"nombre": "Ana", "email": "ana@test.com"})
    assert r.status_code == 400
    assert r.get_json()["error"] == "Faltan campos requeridos"


def test_registro_con_correo_repetido(client):
    registrar(client)
    r = registrar(client, nombre="Otra")
    assert r.status_code == 409
    assert r.get_json()["error"] == "El correo ya está registrado"


def test_login_correcto_devuelve_token_y_usuario_sin_hash(client):
    registrar(client)
    r = iniciar_sesion(client)
    assert r.status_code == 200
    cuerpo = r.get_json()
    assert cuerpo["token"]
    assert cuerpo["usuario"]["email"] == "ana@test.com"
    assert cuerpo["usuario"]["roles"] == ["Usuario"]
    assert "password_hash" not in cuerpo["usuario"]


def test_login_con_contrasena_incorrecta(client):
    registrar(client)
    r = iniciar_sesion(client, password="otra")
    assert r.status_code == 401
    assert r.get_json()["error"] == "Correo o contraseña incorrectos"


def test_login_con_correo_inexistente(client):
    r = iniciar_sesion(client, email="nadie@test.com")
    assert r.status_code == 401
    assert r.get_json()["error"] == "Correo o contraseña incorrectos"
