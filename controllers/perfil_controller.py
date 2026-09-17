from flask import Blueprint, request, jsonify
from models.usuario_model import buscar_por_id, actualizar_perfil, cambiar_password, verificar_password
from models.rol_model import obtener_roles_de_usuario
from middleware.auth_middleware import requiere_token
from views.usuario_view import usuario_a_json

perfil_bp = Blueprint("perfil", __name__)

@perfil_bp.route("/api/users/profile", methods=["GET"])
@requiere_token
def ver_perfil():
    # request.id_usuario lo puso el middleware al validar el token:
    # cada quien ve SOLO su propio perfil, nunca el de otro
    usuario = buscar_por_id(request.id_usuario)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    roles = obtener_roles_de_usuario(usuario["id_usuario"])
    return jsonify({"usuario": usuario_a_json(dict(usuario), roles)}), 200

@perfil_bp.route("/api/users/profile", methods=["PUT"])
@requiere_token
def editar_perfil():
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")

    if not nombre or not email:
        return jsonify({"error": "Nombre y correo son obligatorios"}), 400

    exito, error = actualizar_perfil(request.id_usuario, nombre, email)
    if not exito:
        return jsonify({"error": error}), 409

    usuario = buscar_por_id(request.id_usuario)
    roles = obtener_roles_de_usuario(usuario["id_usuario"])
    return jsonify({"message": "Perfil actualizado", "usuario": usuario_a_json(dict(usuario), roles)}), 200

@perfil_bp.route("/api/auth/change-password", methods=["PUT"])
@requiere_token
def cambiar_contrasena():
    data = request.get_json()
    actual = data.get("current_password")
    nueva = data.get("new_password")

    if not actual or not nueva:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    usuario = buscar_por_id(request.id_usuario)
    if not verificar_password(usuario, actual):
        return jsonify({"error": "La contraseña actual es incorrecta"}), 400

    cambiar_password(request.id_usuario, nueva)
    return jsonify({"message": "Contraseña actualizada"}), 200