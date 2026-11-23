"""Contrato de /api/users: administración de usuarios y reglas por rol."""
from tests.helpers import cabeceras, registrar, usuario_con_rol, usuario_con_token

ADMIN, USUARIO, SUPER = 1, 2, 3


def _correos(client, token):
    r = client.get("/api/users/", headers=cabeceras(token))
    return [u["email"] for u in r.get_json()["usuarios"]]


def test_usuario_comun_no_puede_listar(client):
    _, token = usuario_con_token(client)
    r = client.get("/api/users/", headers=cabeceras(token))
    assert r.status_code == 403


def test_admin_lista_usuarios_con_roles(client, db_path):
    _, token = usuario_con_rol(client, db_path, [ADMIN], "Admin", "admin@test.com")
    registrar(client, "Luis", "luis@test.com")
    r = client.get("/api/users/", headers=cabeceras(token))
    assert r.status_code == 200
    usuarios = r.get_json()["usuarios"]
    assert {u["email"] for u in usuarios} == {"admin@test.com", "luis@test.com"}
    assert all("password_hash" not in u for u in usuarios)
    assert next(u for u in usuarios if u["email"] == "admin@test.com")["roles"] == ["Administrador"]


def test_estadisticas(client, db_path):
    _, token = usuario_con_rol(client, db_path, [ADMIN], "Admin", "admin@test.com")
    registrar(client, "Luis", "luis@test.com")
    r = client.get("/api/users/stats", headers=cabeceras(token))
    assert r.status_code == 200
    cuerpo = r.get_json()
    assert cuerpo["total"] == 2
    assert cuerpo["por_rol"]["Administrador"] == 1
    assert cuerpo["por_rol"]["Usuario"] == 1


def test_admin_puede_promover_a_un_usuario_comun(client, db_path):
    _, token = usuario_con_rol(client, db_path, [ADMIN], "Admin", "admin@test.com")
    id_luis = registrar(client, "Luis", "luis@test.com").get_json()["id_usuario"]
    r = client.put(f"/api/users/{id_luis}/roles", headers=cabeceras(token), json={"role_ids": [ADMIN]})
    assert r.status_code == 200


def test_admin_no_puede_tocar_a_otro_admin(client, db_path):
    _, token = usuario_con_rol(client, db_path, [ADMIN], "Admin", "admin@test.com")
    id_otro, _ = usuario_con_rol(client, db_path, [ADMIN], "Otro", "otro@test.com")
    r = client.put(f"/api/users/{id_otro}/roles", headers=cabeceras(token), json={"role_ids": [USUARIO]})
    assert r.status_code == 403
    assert r.get_json()["error"] == "Solo un SuperAdministrador puede modificar este rol"


def test_admin_no_puede_otorgar_superadmin(client, db_path):
    _, token = usuario_con_rol(client, db_path, [ADMIN], "Admin", "admin@test.com")
    id_luis = registrar(client, "Luis", "luis@test.com").get_json()["id_usuario"]
    r = client.put(f"/api/users/{id_luis}/roles", headers=cabeceras(token), json={"role_ids": [SUPER]})
    assert r.status_code == 403
    assert r.get_json()["error"] == "No tienes permisos para asignar ese rol"


def test_superadmin_puede_cambiar_cualquier_rol(client, db_path):
    _, token = usuario_con_rol(client, db_path, [SUPER], "Super", "super@test.com")
    id_otro, _ = usuario_con_rol(client, db_path, [ADMIN], "Otro", "otro@test.com")
    r = client.put(f"/api/users/{id_otro}/roles", headers=cabeceras(token), json={"role_ids": [USUARIO]})
    assert r.status_code == 200


def test_solo_superadmin_elimina_usuarios(client, db_path):
    _, token_admin = usuario_con_rol(client, db_path, [ADMIN], "Admin", "admin@test.com")
    id_luis = registrar(client, "Luis", "luis@test.com").get_json()["id_usuario"]
    r = client.delete(f"/api/users/{id_luis}", headers=cabeceras(token_admin))
    assert r.status_code == 403


def test_superadmin_elimina_a_otro_usuario(client, db_path):
    _, token = usuario_con_rol(client, db_path, [SUPER], "Super", "super@test.com")
    id_luis = registrar(client, "Luis", "luis@test.com").get_json()["id_usuario"]
    r = client.delete(f"/api/users/{id_luis}", headers=cabeceras(token))
    assert r.status_code == 200
    assert "luis@test.com" not in _correos(client, token)


def test_superadmin_no_puede_eliminarse_a_si_mismo(client, db_path):
    id_super, token = usuario_con_rol(client, db_path, [SUPER], "Super", "super@test.com")
    r = client.delete(f"/api/users/{id_super}", headers=cabeceras(token))
    assert r.status_code == 400
    assert r.get_json()["error"] == "No puedes eliminar tu propia cuenta"
