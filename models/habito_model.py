from datetime import date
from models.database import get_connection


def crear_habito(id_usuario, descripcion, categoria, fecha=None):
    # Si no llega fecha, el hábito es para hoy. Con fecha se pueden programar días futuros.
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO habito (id_usuario, descripcion, categoria, fecha) VALUES (?, ?, ?, ?)",
        (id_usuario, descripcion, categoria, fecha or date.today().isoformat())
    )
    nuevo_id = cur.lastrowid
    conn.commit()
    conn.close()
    return nuevo_id


def obtener_habitos_de_usuario(id_usuario, fecha=None):
    conn = get_connection()
    cur = conn.cursor()
    # Solo los hábitos de ESE usuario: nunca los de otro
    sql = "SELECT id, descripcion, categoria, fecha, completado FROM habito WHERE id_usuario = ?"
    params = [id_usuario]
    if fecha:
        # date() ignora la hora, por si alguna fecha guardada la trae
        sql += " AND date(fecha) = ?"
        params.append(fecha)
    sql += " ORDER BY id DESC"
    cur.execute(sql, params)
    habitos = []
    for row in cur.fetchall():
        h = dict(row)
        # SQLite guarda 0/1; la app necesita true/false
        h["completado"] = bool(h["completado"])
        habitos.append(h)
    conn.close()
    return habitos


def marcar_completado(id_habito, id_usuario, completado):
    conn = get_connection()
    cur = conn.cursor()
    # El "AND id_usuario" evita que alguien marque hábitos de otro usuario
    cur.execute(
        "UPDATE habito SET completado = ? WHERE id = ? AND id_usuario = ?",
        (1 if completado else 0, id_habito, id_usuario)
    )
    modificado = cur.rowcount > 0
    conn.commit()
    conn.close()
    return modificado


def resumen_por_dias(id_usuario, desde, hasta):
    # Por cada día con hábitos: cuántos hay y cuántos se cumplieron (para las llamas del calendario)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT date(fecha) AS fecha,
               COUNT(*) AS total,
               SUM(completado) AS completados
        FROM habito
        WHERE id_usuario = ? AND date(fecha) BETWEEN ? AND ?
        GROUP BY date(fecha)
        ORDER BY date(fecha)
        """,
        (id_usuario, desde, hasta)
    )
    dias = [
        {"fecha": r["fecha"], "total": r["total"], "completados": r["completados"] or 0}
        for r in cur.fetchall()
    ]
    conn.close()
    return dias