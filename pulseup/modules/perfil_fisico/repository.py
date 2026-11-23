"""SQL del perfil físico (una fila por usuario)."""


def buscar(conn, id_usuario):
    return conn.execute("SELECT * FROM perfil_fisico WHERE id_usuario = ?", (id_usuario,)).fetchone()


def guardar(conn, id_usuario, datos, actualizado_en):
    """Crea el perfil o reemplaza el existente (upsert por id_usuario)."""
    conn.execute(
        """
        INSERT INTO perfil_fisico
            (id_usuario, fecha_nacimiento, sexo, peso_kg, estatura_cm, nivel, actualizado_en)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (id_usuario) DO UPDATE SET
            fecha_nacimiento = excluded.fecha_nacimiento,
            sexo = excluded.sexo,
            peso_kg = excluded.peso_kg,
            estatura_cm = excluded.estatura_cm,
            nivel = excluded.nivel,
            actualizado_en = excluded.actualizado_en
        """,
        (
            id_usuario,
            datos["fecha_nacimiento"],
            datos["sexo"],
            datos["peso_kg"],
            datos["estatura_cm"],
            datos["nivel"],
            actualizado_en,
        ),
    )


def eliminar_de_usuario(conn, id_usuario):
    conn.execute("DELETE FROM perfil_fisico WHERE id_usuario = ?", (id_usuario,))
