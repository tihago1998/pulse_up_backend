"""Contrato del perfil y del cambio de contraseña."""
from tests.helpers import cabeceras, iniciar_sesion, registrar, usuario_con_token


def test_perfil_exige_token(client):
    assert client.get("/api/users/profile").status_code == 401
    r = client.get("/api/users/profile", headers={"Authorization": "Bearer basura"})
    assert r.status_code == 401
    assert r.get_json()["error"] == "Token inválido"


def test_ver_perfil(client):
    _, token = usuario_con_token(client)
    r = client.get("/api/users/profile", headers=cabeceras(token))
    assert r.status_code == 200
    assert r.get_json()["usuario"]["nombre"] == "Ana"


def test_editar_perfil(client):
    _, token = usuario_con_token(client)
    r = client.put("/api/users/profile", headers=cabeceras(token),
                   json={"nombre": "Ana Maria", "email": "nueva@test.com"})
    assert r.status_code == 200
    assert r.get_json()["usuario"]["nombre"] == "Ana Maria"
    assert r.get_json()["usuario"]["email"] == "nueva@test.com"


def test_editar_perfil_con_correo_de_otro_usuario(client):
    registrar(client, "Luis", "luis@test.com")
    _, token = usuario_con_token(client)
    r = client.put("/api/users/profile", headers=cabeceras(token),
                   json={"nombre": "Ana", "email": "luis@test.com"})
    assert r.status_code == 409
    assert r.get_json()["error"] == "Ese correo ya está en uso"


def test_editar_perfil_con_campos_faltantes(client):
    _, token = usuario_con_token(client)
    r = client.put("/api/users/profile", headers=cabeceras(token), json={"nombre": "Ana"})
    assert r.status_code == 400


def test_cambiar_contrasena(client):
    _, token = usuario_con_token(client)
    r = client.put("/api/auth/change-password", headers=cabeceras(token),
                   json={"current_password": "clave123", "new_password": "nueva456"})
    assert r.status_code == 200
    assert iniciar_sesion(client, password="clave123").status_code == 401
    assert iniciar_sesion(client, password="nueva456").status_code == 200


def test_cambiar_contrasena_con_actual_incorrecta(client):
    _, token = usuario_con_token(client)
    r = client.put("/api/auth/change-password", headers=cabeceras(token),
                   json={"current_password": "mala", "new_password": "nueva456"})
    assert r.status_code == 400
    assert r.get_json()["error"] == "La contraseña actual es incorrecta"


def test_cambiar_contrasena_con_campos_faltantes(client):
    _, token = usuario_con_token(client)
    r = client.put("/api/auth/change-password", headers=cabeceras(token), json={"current_password": "x"})
    assert r.status_code == 400
