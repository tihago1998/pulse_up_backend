from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_connection

def buscar_por_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuario WHERE email = ?", (email,))
    usuario = cur.fetchone()
    conn.close()
    return usuario

def crear_usuario(nombre, email, password):
    conn = get_connection()
    cur = conn.cursor()

    password_hash = generate_password_hash(password)
    cur.execute(
        "INSERT INTO usuario (nombre, email, password_hash) VALUES (?, ?, ?)",
        (nombre, email, password_hash)
    )
    id_usuario = cur.lastrowid

    # Nace con rol Usuario (id 2) por defecto
    cur.execute("INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (?, 2)", (id_usuario,))

    conn.commit()
    conn.close()
    return id_usuario

def verificar_password(usuario_row, password):
    return check_password_hash(usuario_row["password_hash"], password)

def obtener_todos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_usuario, nombre, email FROM usuario")
    usuarios = [dict(row) for row in cur.fetchall()]
    conn.close()
    return usuarios

def actualizar_roles(id_usuario, role_ids):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuario_rol WHERE id_usuario = ?", (id_usuario,))
    for id_rol in role_ids:
        cur.execute("INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (?, ?)", (id_usuario, id_rol))
    conn.commit()
    conn.close()