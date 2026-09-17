from datetime import date
from models.database import get_connection

def crear_habito(id_usuario, descripcion, categoria):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO habito (id_usuario, descripcion, categoria, fecha) VALUES (?, ?, ?, ?)",
        (id_usuario, descripcion, categoria, date.today().isoformat())
    )
    nuevo_id = cur.lastrowid
    conn.commit()
    conn.close()
    return nuevo_id

def obtener_habitos_de_usuario(id_usuario):
    conn = get_connection()
    cur = conn.cursor()
    # Solo los hábitos de ESE usuario: nunca los de otro
    cur.execute(
        "SELECT id, descripcion, categoria, fecha FROM habito WHERE id_usuario = ? ORDER BY id DESC",
        (id_usuario,)
    )
    habitos = [dict(row) for row in cur.fetchall()]
    conn.close()
    return habitos