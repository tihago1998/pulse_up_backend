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


def ejercicios_de_grupo(client, token, grupo):
    r = client.get(f"/api/ejercicios/?musculo={grupo}", headers=cabeceras(token))
    return r.get_json()["ejercicios"]


def crear_rutina(client, token, ids_ejercicios, nombre="Rutina de prueba"):
    """Crea una rutina propia con esos ejercicios y devuelve su id."""
    cuerpo = {
        "nombre": nombre,
        "ejercicios": [{"id_ejercicio": i, "series": 3, "repeticiones": "10"} for i in ids_ejercicios],
    }
    r = client.post("/api/rutinas/", json=cuerpo, headers=cabeceras(token))
    assert r.status_code == 201, r.get_json()
    return r.get_json()["id"]


def rutina_de_grupos(client, token, *grupos, nombre=None):
    """Rutina propia con un ejercicio cuyo grupo principal es cada uno de `grupos`."""
    ids = [ejercicios_de_grupo(client, token, g)[0]["id"] for g in grupos]
    return crear_rutina(client, token, ids, nombre or "Rutina " + " y ".join(grupos))
