"""SQL del catálogo de ejercicios."""

# Miniatura = foto de la posición inicial (orden 0), o NULL si el ejercicio aún no tiene fotos
_SELECT_CON_MINIATURA = """
    SELECT e.*,
           (SELECT url FROM ejercicio_imagen i WHERE i.ejercicio_id = e.id AND i.orden = 0) AS imagen_miniatura
    FROM ejercicio e
"""


def _filtros_sql(musculo=None, equipo=None, nivel=None, texto=None, ambiente=None):
    condiciones, params = [], []
    if musculo:
        condiciones.append("e.grupo_muscular = ?")
        params.append(musculo)
    if equipo:
        condiciones.append("e.equipo = ?")
        params.append(equipo)
    if nivel:
        condiciones.append("e.nivel = ?")
        params.append(nivel)
    if texto:
        condiciones.append("e.nombre LIKE ?")
        params.append(f"%{texto}%")
    if ambiente:
        # ambientes es una lista JSON en texto: ["gimnasio", "casa"]
        condiciones.append("EXISTS (SELECT 1 FROM json_each(e.ambientes) WHERE json_each.value = ?)")
        params.append(ambiente)
    where = (" WHERE " + " AND ".join(condiciones)) if condiciones else ""
    return where, params


def listar(conn, musculo=None, equipo=None, nivel=None, texto=None, ambiente=None, limit=None, offset=0):
    where, params = _filtros_sql(musculo, equipo, nivel, texto, ambiente)
    sql = _SELECT_CON_MINIATURA + where + " ORDER BY e.grupo_muscular, e.nombre"
    if limit is not None:
        sql += " LIMIT ? OFFSET ?"
        params += [limit, offset]
    return conn.execute(sql, params).fetchall()


def contar(conn, musculo=None, equipo=None, nivel=None, texto=None, ambiente=None):
    where, params = _filtros_sql(musculo, equipo, nivel, texto, ambiente)
    return conn.execute("SELECT COUNT(*) FROM ejercicio e" + where, params).fetchone()[0]


def buscar_por_id(conn, id_ejercicio):
    return conn.execute("SELECT * FROM ejercicio WHERE id = ?", (id_ejercicio,)).fetchone()


def imagenes(conn, id_ejercicio):
    return conn.execute(
        "SELECT orden, url FROM ejercicio_imagen WHERE ejercicio_id = ? ORDER BY orden", (id_ejercicio,)
    ).fetchall()


def creditos(conn):
    return conn.execute(
        """
        SELECT fuente, licencia, autor, atribucion, COUNT(*) AS imagenes
        FROM ejercicio_imagen
        GROUP BY fuente, licencia, autor, atribucion
        ORDER BY fuente
        """
    ).fetchall()


def valores_distintos(conn, columna):
    # `columna` viene siempre del código (nunca del usuario), por eso es seguro interpolarla
    filas = conn.execute(f"SELECT DISTINCT {columna} AS valor FROM ejercicio ORDER BY valor").fetchall()
    return [f["valor"] for f in filas]


def ambientes_usados(conn):
    filas = conn.execute(
        "SELECT DISTINCT json_each.value AS valor FROM ejercicio, json_each(ejercicio.ambientes)"
    ).fetchall()
    return {f["valor"] for f in filas}


def ids_existentes(conn, ids):
    if not ids:
        return set()
    marcas = ",".join("?" * len(ids))
    filas = conn.execute(f"SELECT id FROM ejercicio WHERE id IN ({marcas})", list(ids)).fetchall()
    return {f["id"] for f in filas}
