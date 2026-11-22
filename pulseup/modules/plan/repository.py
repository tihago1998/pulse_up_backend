"""SQL del plan semanal y de las sesiones (rutinas del día marcadas como cumplidas)."""


# ---- Plan semanal -------------------------------------------------------------

def listar(conn, id_usuario):
    """Días con rutina del usuario (los que faltan son descanso)."""
    return conn.execute(
        """
        SELECT p.dia_semana, p.id_rutina, p.creado_en, r.nombre
        FROM plan_dia p
        JOIN rutina r ON r.id = p.id_rutina
        WHERE p.id_usuario = ?
        ORDER BY p.dia_semana
        """,
        (id_usuario,),
    ).fetchall()


def buscar_dia(conn, id_usuario, dia_semana):
    return conn.execute(
        """
        SELECT p.dia_semana, p.id_rutina, p.creado_en, r.nombre
        FROM plan_dia p
        JOIN rutina r ON r.id = p.id_rutina
        WHERE p.id_usuario = ? AND p.dia_semana = ?
        """,
        (id_usuario, dia_semana),
    ).fetchone()


def asignar(conn, id_usuario, dia_semana, id_rutina, creado_en):
    """Crea o reemplaza la rutina del día. Al reemplazar se conserva `creado_en`:
    el día sigue siendo de entrenamiento desde la primera vez que se planificó."""
    conn.execute(
        """
        INSERT INTO plan_dia (id_usuario, dia_semana, id_rutina, creado_en)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (id_usuario, dia_semana) DO UPDATE SET id_rutina = excluded.id_rutina
        """,
        (id_usuario, dia_semana, id_rutina, creado_en),
    )


def quitar(conn, id_usuario, dia_semana):
    conn.execute("DELETE FROM plan_dia WHERE id_usuario = ? AND dia_semana = ?", (id_usuario, dia_semana))


def rutina_en_algun_plan(conn, id_rutina):
    return conn.execute("SELECT 1 FROM plan_dia WHERE id_rutina = ? LIMIT 1", (id_rutina,)).fetchone() is not None


def grupos_por_rutina(conn, ids_rutina):
    """{id_rutina: {grupos musculares principales de sus ejercicios}}."""
    ids = list(set(ids_rutina))
    if not ids:
        return {}
    marcas = ",".join("?" * len(ids))
    filas = conn.execute(
        f"""
        SELECT DISTINCT re.id_rutina, e.grupo_muscular
        FROM rutina_ejercicio re
        JOIN ejercicio e ON e.id = re.id_ejercicio
        WHERE re.id_rutina IN ({marcas})
        """,
        ids,
    ).fetchall()
    resultado = {i: set() for i in ids}
    for f in filas:
        resultado[f["id_rutina"]].add(f["grupo_muscular"])
    return resultado


# ---- Sesiones -----------------------------------------------------------------

def buscar_sesion(conn, id_usuario, fecha):
    return conn.execute(
        "SELECT * FROM sesion WHERE id_usuario = ? AND fecha = ?", (id_usuario, fecha)
    ).fetchone()


def crear_sesion(conn, id_usuario, fecha, id_rutina, completada_en):
    conn.execute(
        "INSERT INTO sesion (id_usuario, fecha, id_rutina, completada_en) VALUES (?, ?, ?, ?)",
        (id_usuario, fecha, id_rutina, completada_en),
    )


def sesiones_entre(conn, id_usuario, desde, hasta):
    """Sesiones del rango con el nombre de la rutina (None si la rutina ya no existe)."""
    return conn.execute(
        """
        SELECT s.fecha, s.id_rutina, r.nombre
        FROM sesion s
        LEFT JOIN rutina r ON r.id = s.id_rutina
        WHERE s.id_usuario = ? AND s.fecha BETWEEN ? AND ?
        ORDER BY s.fecha
        """,
        (id_usuario, desde, hasta),
    ).fetchall()


def fechas_con_sesion(conn, id_usuario):
    filas = conn.execute("SELECT fecha FROM sesion WHERE id_usuario = ?", (id_usuario,)).fetchall()
    return {f["fecha"] for f in filas}


# ---- Limpieza -----------------------------------------------------------------

def eliminar_de_usuario(conn, id_usuario):
    """Borra el plan y las sesiones del usuario (al eliminar su cuenta)."""
    conn.execute("DELETE FROM sesion WHERE id_usuario = ?", (id_usuario,))
    conn.execute("DELETE FROM plan_dia WHERE id_usuario = ?", (id_usuario,))
