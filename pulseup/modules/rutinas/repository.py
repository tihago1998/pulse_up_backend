"""SQL de rutinas y de los ejercicios que contienen."""

_BASE = """
    SELECT r.*, (SELECT COUNT(*) FROM rutina_ejercicio re WHERE re.id_rutina = r.id) AS total_ejercicios
    FROM rutina r
"""

# Un ejercicio de una rutina con los datos del catálogo que muestra el plan
_ITEM = """
    SELECT re.id AS item_id, re.id_rutina, re.id_ejercicio, re.orden, re.series, re.repeticiones,
           re.unidad, re.peso_kg, re.descanso_seg,
           e.nombre, e.grupo_muscular, e.met, COALESCE(e.musculo_principal, e.grupo_muscular) AS musculo_principal,
           (SELECT url FROM ejercicio_imagen i WHERE i.ejercicio_id = e.id AND i.orden = 0) AS imagen_miniatura
    FROM rutina_ejercicio re
    JOIN ejercicio e ON e.id = re.id_ejercicio
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
        SELECT re.orden, re.series, re.repeticiones, re.descanso_seg, re.peso_kg, re.unidad, e.*
        FROM rutina_ejercicio re
        JOIN ejercicio e ON e.id = re.id_ejercicio
        WHERE re.id_rutina = ?
        ORDER BY re.orden
        """,
        (id_rutina,),
    ).fetchall()


def crear(conn, id_usuario, nombre, descripcion, objetivo, nivel, duracion_min, items, origen=None):
    id_rutina = conn.execute(
        """
        INSERT INTO rutina (id_usuario, nombre, descripcion, objetivo, nivel, duracion_min, origen)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (id_usuario, nombre, descripcion, objetivo, nivel, duracion_min, origen),
    ).lastrowid
    for orden, it in enumerate(items, start=1):
        agregar_item(conn, id_rutina, orden, it)
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


# ---- Ejercicios de una rutina (los usa el plan semanal) ---------------------------------

def items_de_rutinas(conn, ids_rutina):
    """{id_rutina: [ejercicios en orden]} con nombre, músculo y miniatura del catálogo."""
    ids = list(set(ids_rutina))
    resultado = {i: [] for i in ids}
    if not ids:
        return resultado
    marcas = ",".join("?" * len(ids))
    filas = conn.execute(_ITEM + f" WHERE re.id_rutina IN ({marcas}) ORDER BY re.id_rutina, re.orden", ids)
    for f in filas.fetchall():
        resultado[f["id_rutina"]].append(f)
    return resultado


def buscar_item(conn, item_id):
    return conn.execute(_ITEM + " WHERE re.id = ?", (item_id,)).fetchone()


def item_por_orden(conn, id_rutina, orden):
    return conn.execute(_ITEM + " WHERE re.id_rutina = ? AND re.orden = ?", (id_rutina, orden)).fetchone()


def contiene_ejercicio(conn, id_rutina, id_ejercicio):
    return conn.execute(
        "SELECT 1 FROM rutina_ejercicio WHERE id_rutina = ? AND id_ejercicio = ? LIMIT 1", (id_rutina, id_ejercicio)
    ).fetchone() is not None


def siguiente_orden(conn, id_rutina):
    return conn.execute(
        "SELECT COALESCE(MAX(orden), 0) + 1 FROM rutina_ejercicio WHERE id_rutina = ?", (id_rutina,)
    ).fetchone()[0]


def agregar_item(conn, id_rutina, orden, it):
    return conn.execute(
        """
        INSERT INTO rutina_ejercicio
            (id_rutina, id_ejercicio, orden, series, repeticiones, descanso_seg, peso_kg, unidad)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id_rutina, it["id_ejercicio"], orden, it["series"], it["repeticiones"], it["descanso_seg"],
            it.get("peso_kg"), it.get("unidad") or "repeticiones",
        ),
    ).lastrowid


def actualizar_item(conn, item_id, cambios):
    """`cambios` solo trae columnas conocidas del servicio (series, repeticiones, peso_kg, unidad, descanso_seg)."""
    if not cambios:
        return
    asignaciones = ", ".join(f"{campo} = ?" for campo in cambios)
    conn.execute(f"UPDATE rutina_ejercicio SET {asignaciones} WHERE id = ?", [*cambios.values(), item_id])


def quitar_item(conn, item_id):
    conn.execute("DELETE FROM rutina_ejercicio WHERE id = ?", (item_id,))


def copiar(conn, id_rutina, id_usuario, nombre, origen):
    """Copia la rutina (datos y ejercicios con su orden) como rutina propia del usuario. Devuelve el id nuevo."""
    nuevo_id = conn.execute(
        """
        INSERT INTO rutina (id_usuario, nombre, descripcion, objetivo, nivel, duracion_min, origen)
        SELECT ?, ?, descripcion, objetivo, nivel, duracion_min, ? FROM rutina WHERE id = ?
        """,
        (id_usuario, nombre, origen, id_rutina),
    ).lastrowid
    conn.execute(
        """
        INSERT INTO rutina_ejercicio
            (id_rutina, id_ejercicio, orden, series, repeticiones, descanso_seg, peso_kg, unidad)
        SELECT ?, id_ejercicio, orden, series, repeticiones, descanso_seg, peso_kg, unidad
        FROM rutina_ejercicio WHERE id_rutina = ?
        """,
        (nuevo_id, id_rutina),
    )
    return nuevo_id
