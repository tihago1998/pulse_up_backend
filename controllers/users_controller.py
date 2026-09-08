from flask import Blueprint, request, jsonify
from models.usuario_model import obtener_todos, actualizar_roles
from models.rol_model import obtener_roles_de_usuario
from middleware.auth_middleware import requiere_token, requiere_admin
from views.usuario_view import usuario_a_json, lista_usuarios_a_json

users_bp = Blueprint("users", __name__)

@users_bp.route("/api/users/", methods=["GET"])
@requiere_token   # primero valida que haya un token válido (usuario autenticado)
@requiere_admin   # luego valida que ese usuario tenga rol Administrador
def listar_usuarios():
    usuarios = obtener_todos()
    usuarios_con_roles = [
        usuario_a_json(u, obtener_roles_de_usuario(u["id_usuario"]))
        for u in usuarios
    ]
    return jsonify(lista_usuarios_a_json(usuarios_con_roles)), 200

@users_bp.route("/api/users/<int:id_usuario>/roles", methods=["PUT"])
@requiere_token
@requiere_admin
def asignar_rol(id_usuario):
    # <int:id_usuario> en la ruta captura el número que venga en la URL,
    # por ejemplo /api/users/7/roles -> id_usuario = 7
    data = request.get_json()
    role_ids = data.get("role_ids", [])  # ej: [1] para hacerlo Administrador

    actualizar_roles(id_usuario, role_ids)

    return jsonify({"message": "Roles actualizados"}), 200