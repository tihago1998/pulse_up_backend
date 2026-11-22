"""SQL de hábitos. Siempre filtra por usuario: nadie ve ni toca los de otro."""


def crear(conn, id_usuario, descripcion, categoria, fecha):
    cur = conn.execute(
        "INSERT INTO habito (id_usuario, descripcion, categoria, fecha) VALUES (?, ?, ?, ?)",
        (id_usuario, descripcion, categoria, fecha),
    )
    return cur.lastrowid


def listar(conn, id_usuario, fecha=None):
    sql = "SELECT id, descripcion, categoria, fecha, completado FROM habito WHERE id_usuario = ?"
    params = [id_usuario]
    if fecha:
        # date() ignora la hora, por si alguna fecha guardada la trae
        sql += " AND date(fecha) = ?"
        params.append(fecha)
    sql += " ORDER BY id DESC"
    habitos = []
    for fila in conn.execute(sql, params).fetchall():
        habito = dict(fila)
        habito["completado"] = bool(habito["completado"])  # SQLite guarda 0/1
        habitos.append(habito)
    return habitos


def marcar_completado(conn, id_habito, id_usuario, completado):
    cur = conn.execute(
        "UPDATE habito SET completado = ? WHERE id = ? AND id_usuario = ?",
        (1 if completado else 0, id_habito, id_usuario),
    )
    return cur.rowcount > 0


def resumen_por_dias(conn, id_usuario, desde, hasta):
    filas = conn.execute(
        """
        SELECT date(fecha) AS fecha, COUNT(*) AS total, SUM(completado) AS completados
        FROM habito
        WHERE id_usuario = ? AND date(fecha) BETWEEN ? AND ?
        GROUP BY date(fecha)
        ORDER BY date(fecha)
        """,
        (id_usuario, desde, hasta),
    ).fetchall()
    return [{"fecha": f["fecha"], "total": f["total"], "completados": f["completados"] or 0} for f in filas]


def eliminar_de_usuario(conn, id_usuario):
    conn.execute("DELETE FROM habito WHERE id_usuario = ?", (id_usuario,))
