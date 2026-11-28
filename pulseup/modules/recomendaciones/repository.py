"""SQL de las reglas de recomendación y de las proporciones de fuerza."""


def regla(conn, tipo, nivel):
    fila = conn.execute(
        "SELECT * FROM recomendacion_regla WHERE tipo = ? AND nivel = ?", (tipo, nivel)
    ).fetchone()
    return dict(fila) if fila is not None else None


def ratio(conn, clave, sexo, nivel):
    """Proporción 1RM / peso corporal. Primero la del sexo pedido; si no hay, la de 'todos' (prensa)."""
    fila = conn.execute(
        """
        SELECT ratio FROM referencia_fuerza_ratio
        WHERE clave = ? AND nivel = ? AND sexo IN (?, 'todos')
        ORDER BY CASE WHEN sexo = ? THEN 0 ELSE 1 END
        LIMIT 1
        """,
        (clave, nivel, sexo, sexo),
    ).fetchone()
    return fila["ratio"] if fila is not None else None


# ---- Carga completa (una sola vez por petición, para el listado de ejercicios) -------------

def todas_las_reglas(conn):
    """{(tipo, nivel): regla} con todas las reglas."""
    return {(f["tipo"], f["nivel"]): dict(f) for f in conn.execute("SELECT * FROM recomendacion_regla").fetchall()}


def todas_las_ratios(conn):
    """{(clave, sexo, nivel): ratio} con todas las proporciones de fuerza."""
    filas = conn.execute("SELECT clave, sexo, nivel, ratio FROM referencia_fuerza_ratio").fetchall()
    return {(f["clave"], f["sexo"], f["nivel"]): f["ratio"] for f in filas}


def ratio_en(ratios, clave, sexo, nivel):
    """Lo mismo que ratio(), pero sobre las proporciones ya cargadas: primero la del sexo, luego 'todos'."""
    valor = ratios.get((clave, sexo, nivel))
    return valor if valor is not None else ratios.get((clave, "todos", nivel))
