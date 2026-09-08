from flask import Blueprint, request, jsonify
from database import get_connection
from decorators import requiere_token, requiere_admin

users_bp = Blueprint("users", __name__)

@users_bp.route("/api/users/", methods=["GET"])
@requiere_token   # primero valida que haya un token válido (usuario autenticado)
@requiere_admin   # luego valida que ese usuario tenga rol Administrador
def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor()

    # Traemos todos los usuarios (sin exponer el password_hash, por seguridad)
    cur.execute("SELECT id_usuario, nombre, email FROM usuario")
    usuarios = [dict(row) for row in cur.fetchall()]

    # Para cada usuario, buscamos qué roles tiene y se los agregamos a su diccionario
    for u in usuarios:
        cur.execute("""
            SELECT r.nombre_rol FROM rol r
            JOIN usuario_rol ur ON r.id_rol = ur.id_rol
            WHERE ur.id_usuario = ?
        """, (u["id_usuario"],))
        u["roles"] = [row["nombre_rol"] for row in cur.fetchall()]

    conn.close()
    return jsonify({"usuarios": usuarios}), 200

@users_bp.route("/api/users/<int:id_usuario>/roles", methods=["PUT"])
@requiere_token
@requiere_admin
def asignar_rol(id_usuario):
    # <int:id_usuario> en la ruta captura el número que venga en la URL,
    # por ejemplo /api/users/7/roles -> id_usuario = 7
    data = request.get_json()
    role_ids = data.get("role_ids", [])  # ej: [1] para hacerlo Administrador

    conn = get_connection()
    cur = conn.cursor()

    # Borramos los roles actuales de ese usuario...
    cur.execute("DELETE FROM usuario_rol WHERE id_usuario = ?", (id_usuario,))

    # ...y le asignamos los nuevos que llegaron en la petición
    for id_rol in role_ids:
        cur.execute(
            "INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (?, ?)",
            (id_usuario, id_rol)
        )

    conn.commit()
    conn.close()

    return jsonify({"message": "Roles actualizados"}), 200