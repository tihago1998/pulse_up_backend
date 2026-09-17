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

def eliminar_usuario(id_usuario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuario_rol WHERE id_usuario = ?", (id_usuario,))
    cur.execute("DELETE FROM usuario WHERE id_usuario = ?", (id_usuario,))
    conn.commit()
    conn.close()

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

def obtener_estadisticas():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) as total FROM usuario")
    total = cur.fetchone()["total"]

    # Cuenta cuántos usuarios tiene cada rol, uniendo con el nombre del rol
    cur.execute("""
        SELECT r.nombre_rol, COUNT(ur.id_usuario) as cantidad
        FROM rol r
        LEFT JOIN usuario_rol ur ON r.id_rol = ur.id_rol
        GROUP BY r.id_rol
    """)
    por_rol = {row["nombre_rol"]: row["cantidad"] for row in cur.fetchall()}

    conn.close()
    return {"total": total, "por_rol": por_rol}

def actualizar_perfil(id_usuario, nombre, email):
    conn = get_connection()
    cur = conn.cursor()

    # Si el correo nuevo ya lo usa OTRO usuario, no se permite (evita duplicados)
    cur.execute("SELECT id_usuario FROM usuario WHERE email = ? AND id_usuario != ?", (email, id_usuario))
    if cur.fetchone():
        conn.close()
        return False, "Ese correo ya está en uso"

    cur.execute(
        "UPDATE usuario SET nombre = ?, email = ? WHERE id_usuario = ?",
        (nombre, email, id_usuario)
    )
    conn.commit()
    conn.close()
    return True, None

def buscar_por_id(id_usuario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuario WHERE id_usuario = ?", (id_usuario,))
    usuario = cur.fetchone()
    conn.close()
    return usuario

def cambiar_password(id_usuario, password_nuevo):
    conn = get_connection()
    cur = conn.cursor()
    nuevo_hash = generate_password_hash(password_nuevo)
    cur.execute("UPDATE usuario SET password_hash = ? WHERE id_usuario = ?", (nuevo_hash, id_usuario))
    conn.commit()
    conn.close()