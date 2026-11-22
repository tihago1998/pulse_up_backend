"""SQL del catálogo de ejercicios."""


def listar(conn, musculo=None, equipo=None, nivel=None, texto=None):
    sql = "SELECT * FROM ejercicio WHERE 1=1"
    params = []
    if musculo:
        sql += " AND grupo_muscular = ?"
        params.append(musculo)
    if equipo:
        sql += " AND equipo = ?"
        params.append(equipo)
    if nivel:
        sql += " AND nivel = ?"
        params.append(nivel)
    if texto:
        sql += " AND nombre LIKE ?"
        params.append(f"%{texto}%")
    sql += " ORDER BY grupo_muscular, nombre"
    return conn.execute(sql, params).fetchall()


def buscar_por_id(conn, id_ejercicio):
    return conn.execute("SELECT * FROM ejercicio WHERE id = ?", (id_ejercicio,)).fetchone()


def valores_distintos(conn, columna):
    # `columna` viene siempre del código (nunca del usuario), por eso es seguro interpolarla
    filas = conn.execute(f"SELECT DISTINCT {columna} AS valor FROM ejercicio ORDER BY valor").fetchall()
    return [f["valor"] for f in filas]


def ids_existentes(conn, ids):
    if not ids:
        return set()
    marcas = ",".join("?" * len(ids))
    filas = conn.execute(f"SELECT id FROM ejercicio WHERE id IN ({marcas})", list(ids)).fetchall()
    return {f["id"] for f in filas}
