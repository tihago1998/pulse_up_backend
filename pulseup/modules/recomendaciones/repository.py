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
