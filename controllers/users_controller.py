from flask import Blueprint, request, jsonify
from models.usuario_model import obtener_todos, actualizar_roles, eliminar_usuario
from models.rol_model import obtener_roles_de_usuario
from middleware.auth_middleware import requiere_token, requiere_admin_o_superadmin, requiere_superadmin
from views.usuario_view import usuario_a_json, lista_usuarios_a_json
from models.usuario_model import obtener_todos, actualizar_roles, eliminar_usuario, obtener_estadisticas

users_bp = Blueprint("users", __name__)

@users_bp.route("/api/users/", methods=["GET"])
@requiere_token
@requiere_admin_o_superadmin
def listar_usuarios():
    usuarios = obtener_todos()
    usuarios_con_roles = [
        usuario_a_json(u, obtener_roles_de_usuario(u["id_usuario"]))
        for u in usuarios
    ]
    return jsonify(lista_usuarios_a_json(usuarios_con_roles)), 200

@users_bp.route("/api/users/<int:id_usuario>/roles", methods=["PUT"])
@requiere_token
@requiere_admin_o_superadmin
def asignar_rol(id_usuario):
    data = request.get_json()
    role_ids = data.get("role_ids", [])

    # La segunda capa de seguridad vive aquí: no basta con ser "algún tipo de admin",
    # importa a QUIÉN se le quiere cambiar el rol.
    roles_del_objetivo = obtener_roles_de_usuario(id_usuario)
    quien_pide_es_superadmin = "SuperAdministrador" in request.roles

    if not quien_pide_es_superadmin:
        # Un Administrador normal solo puede tocar cuentas que hoy son Usuario común
        if "Administrador" in roles_del_objetivo or "SuperAdministrador" in roles_del_objetivo:
            return jsonify({"error": "Solo un SuperAdministrador puede modificar este rol"}), 403
        # Tampoco puede otorgar el rol SuperAdministrador (id 3)
        if 3 in role_ids:
            return jsonify({"error": "No tienes permisos para asignar ese rol"}), 403

    actualizar_roles(id_usuario, role_ids)
    return jsonify({"message": "Roles actualizados"}), 200

@users_bp.route("/api/users/<int:id_usuario>", methods=["DELETE"])
@requiere_token
@requiere_superadmin
def eliminar(id_usuario):
    if id_usuario == request.id_usuario:
        return jsonify({"error": "No puedes eliminar tu propia cuenta"}), 400
    eliminar_usuario(id_usuario)
    return jsonify({"message": "Usuario eliminado"}), 200

@users_bp.route("/api/users/stats", methods=["GET"])
@requiere_token
@requiere_admin_o_superadmin
def estadisticas():
    return jsonify(obtener_estadisticas()), 200