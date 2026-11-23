"""SQL de usuarios y roles. Cada función recibe la conexión abierta por el servicio."""


def buscar_por_email(conn, email):
    return conn.execute("SELECT * FROM usuario WHERE email = ?", (email,)).fetchone()


def buscar_por_id(conn, id_usuario):
    return conn.execute("SELECT * FROM usuario WHERE id_usuario = ?", (id_usuario,)).fetchone()


def crear(conn, nombre, email, password_hash, id_rol):
    cur = conn.execute(
        "INSERT INTO usuario (nombre, email, password_hash) VALUES (?, ?, ?)",
        (nombre, email, password_hash),
    )
    id_usuario = cur.lastrowid
    conn.execute("INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (?, ?)", (id_usuario, id_rol))
    return id_usuario


def listar(conn):
    filas = conn.execute("SELECT id_usuario, nombre, email FROM usuario").fetchall()
    return [dict(f) for f in filas]


def roles_de_usuario(conn, id_usuario):
    filas = conn.execute(
        """
        SELECT r.nombre_rol FROM rol r
        JOIN usuario_rol ur ON r.id_rol = ur.id_rol
        WHERE ur.id_usuario = ?
        """,
        (id_usuario,),
    ).fetchall()
    return [f["nombre_rol"] for f in filas]


def roles_de_todos(conn):
    """Un solo query: {id_usuario: [nombres de rol]}."""
    filas = conn.execute(
        """
        SELECT ur.id_usuario, r.nombre_rol FROM usuario_rol ur
        JOIN rol r ON r.id_rol = ur.id_rol
        """
    ).fetchall()
    resultado = {}
    for f in filas:
        resultado.setdefault(f["id_usuario"], []).append(f["nombre_rol"])
    return resultado


def ids_de_roles_existentes(conn):
    return {f["id_rol"] for f in conn.execute("SELECT id_rol FROM rol").fetchall()}


def reemplazar_roles(conn, id_usuario, role_ids):
    conn.execute("DELETE FROM usuario_rol WHERE id_usuario = ?", (id_usuario,))
    for id_rol in role_ids:
        conn.execute("INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (?, ?)", (id_usuario, id_rol))


def eliminar_habitos_legado(conn, id_usuario):
    """Borra las filas de la tabla `habito`, sin uso desde que se retiró el módulo de hábitos.

    Se mantiene para no dejar datos huérfanos (ni violar la clave foránea) al eliminar un usuario
    cuya cuenta tenía hábitos de antes. Se podrá quitar cuando una migración elimine la tabla.
    """
    conn.execute("DELETE FROM habito WHERE id_usuario = ?", (id_usuario,))


def eliminar(conn, id_usuario):
    conn.execute("DELETE FROM usuario_rol WHERE id_usuario = ?", (id_usuario,))
    conn.execute("DELETE FROM usuario WHERE id_usuario = ?", (id_usuario,))


def estadisticas(conn):
    total = conn.execute("SELECT COUNT(*) AS total FROM usuario").fetchone()["total"]
    filas = conn.execute(
        """
        SELECT r.nombre_rol, COUNT(ur.id_usuario) AS cantidad
        FROM rol r
        LEFT JOIN usuario_rol ur ON r.id_rol = ur.id_rol
        GROUP BY r.id_rol
        """
    ).fetchall()
    return {"total": total, "por_rol": {f["nombre_rol"]: f["cantidad"] for f in filas}}


def email_usado_por_otro(conn, email, id_usuario):
    fila = conn.execute(
        "SELECT 1 FROM usuario WHERE email = ? AND id_usuario != ?", (email, id_usuario)
    ).fetchone()
    return fila is not None


def actualizar_perfil(conn, id_usuario, nombre, email):
    conn.execute("UPDATE usuario SET nombre = ?, email = ? WHERE id_usuario = ?", (nombre, email, id_usuario))


def actualizar_password_hash(conn, id_usuario, password_hash):
    conn.execute("UPDATE usuario SET password_hash = ? WHERE id_usuario = ?", (password_hash, id_usuario))
