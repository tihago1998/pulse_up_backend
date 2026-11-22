"""Funciones de apoyo para las pruebas: hablan con la API como lo haría la app."""
import sqlite3


def registrar(client, nombre="Ana", email="ana@test.com", password="clave123"):
    return client.post("/api/auth/register", json={"nombre": nombre, "email": email, "password": password})


def iniciar_sesion(client, email="ana@test.com", password="clave123"):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def cabeceras(token):
    return {"Authorization": f"Bearer {token}"}


def usuario_con_token(client, nombre="Ana", email="ana@test.com", password="clave123"):
    """Registra e inicia sesión. Devuelve (id_usuario, token)."""
    id_usuario = registrar(client, nombre, email, password).get_json()["id_usuario"]
    token = iniciar_sesion(client, email, password).get_json()["token"]
    return id_usuario, token


def usuario_con_rol(client, db_path, role_ids, nombre, email, password="clave123"):
    """Crea un usuario, le asigna roles directamente en la base y devuelve (id, token).

    Se inicia sesión DESPUÉS de cambiar los roles porque el token guarda los roles.
    """
    id_usuario = registrar(client, nombre, email, password).get_json()["id_usuario"]
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM usuario_rol WHERE id_usuario = ?", (id_usuario,))
    for id_rol in role_ids:
        conn.execute("INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (?, ?)", (id_usuario, id_rol))
    conn.commit()
    conn.close()
    token = iniciar_sesion(client, email, password).get_json()["token"]
    return id_usuario, token
