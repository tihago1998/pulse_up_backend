"""SQL de rutinas y de los ejercicios que contienen."""

_BASE = """
    SELECT r.*, (SELECT COUNT(*) FROM rutina_ejercicio re WHERE re.id_rutina = r.id) AS total_ejercicios
    FROM rutina r
"""


def listar_visibles(conn, id_usuario, objetivo=None, nivel=None):
    """Plantillas del sistema + las rutinas propias del usuario."""
    sql = _BASE + " WHERE (r.id_usuario IS NULL OR r.id_usuario = ?)"
    params = [id_usuario]
    if objetivo:
        sql += " AND r.objetivo = ?"
        params.append(objetivo)
    if nivel:
        sql += " AND r.nivel = ?"
        params.append(nivel)
    sql += " ORDER BY (r.id_usuario IS NULL), r.nombre"  # primero las propias
    return conn.execute(sql, params).fetchall()


def buscar_visible(conn, id_rutina, id_usuario):
    return conn.execute(
        _BASE + " WHERE r.id = ? AND (r.id_usuario IS NULL OR r.id_usuario = ?)",
        (id_rutina, id_usuario),
    ).fetchone()


def ejercicios_de_rutina(conn, id_rutina):
    return conn.execute(
        """
        SELECT re.orden, re.series, re.repeticiones, re.descanso_seg, e.*
        FROM rutina_ejercicio re
        JOIN ejercicio e ON e.id = re.id_ejercicio
        WHERE re.id_rutina = ?
        ORDER BY re.orden
        """,
        (id_rutina,),
    ).fetchall()


def crear(conn, id_usuario, nombre, descripcion, objetivo, nivel, duracion_min, items):
    id_rutina = conn.execute(
        """
        INSERT INTO rutina (id_usuario, nombre, descripcion, objetivo, nivel, duracion_min)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (id_usuario, nombre, descripcion, objetivo, nivel, duracion_min),
    ).lastrowid
    for orden, it in enumerate(items, start=1):
        conn.execute(
            """
            INSERT INTO rutina_ejercicio (id_rutina, id_ejercicio, orden, series, repeticiones, descanso_seg)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (id_rutina, it["id_ejercicio"], orden, it["series"], it["repeticiones"], it["descanso_seg"]),
        )
    return id_rutina


def eliminar(conn, id_rutina):
    conn.execute("DELETE FROM rutina_ejercicio WHERE id_rutina = ?", (id_rutina,))
    conn.execute("DELETE FROM rutina WHERE id = ?", (id_rutina,))


def eliminar_de_usuario(conn, id_usuario):
    """Borra las rutinas propias del usuario (las plantillas del sistema no tienen dueño)."""
    conn.execute(
        "DELETE FROM rutina_ejercicio WHERE id_rutina IN (SELECT id FROM rutina WHERE id_usuario = ?)",
        (id_usuario,),
    )
    conn.execute("DELETE FROM rutina WHERE id_usuario = ?", (id_usuario,))
