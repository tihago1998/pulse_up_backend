from models.database import get_connection

def obtener_roles_de_usuario(id_usuario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.nombre_rol FROM rol r
        JOIN usuario_rol ur ON r.id_rol = ur.id_rol
        WHERE ur.id_usuario = ?
    """, (id_usuario,))
    roles = [row["nombre_rol"] for row in cur.fetchall()]
    conn.close()
    return roles