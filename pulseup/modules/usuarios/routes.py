"""Rutas HTTP de usuarios, perfil y cambio de contraseña."""
from flask import Blueprint, g, jsonify, request

from pulseup.core.auth import requiere_admin_o_superadmin, requiere_superadmin, requiere_token
from pulseup.core.validacion import cuerpo_json
from pulseup.modules.usuarios import service

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.get("/api/users/")
@requiere_token
@requiere_admin_o_superadmin
def listar():
    return jsonify({"usuarios": service.listar_usuarios()}), 200


@usuarios_bp.get("/api/users/stats")
@requiere_token
@requiere_admin_o_superadmin
def estadisticas():
    return jsonify(service.estadisticas()), 200


@usuarios_bp.put("/api/users/<int:id_usuario>/roles")
@requiere_token
@requiere_admin_o_superadmin
def asignar_roles(id_usuario):
    role_ids = cuerpo_json(request).get("role_ids", [])
    service.asignar_roles(g.roles, id_usuario, role_ids)
    return jsonify({"message": "Roles actualizados"}), 200


@usuarios_bp.delete("/api/users/<int:id_usuario>")
@requiere_token
@requiere_superadmin
def eliminar(id_usuario):
    service.eliminar_usuario(g.id_usuario, id_usuario)
    return jsonify({"message": "Usuario eliminado"}), 200


@usuarios_bp.get("/api/users/profile")
@requiere_token
def ver_perfil():
    # g.id_usuario lo puso el decorador al validar el token: cada quien ve SOLO su perfil
    return jsonify({"usuario": service.ver_perfil(g.id_usuario)}), 200


@usuarios_bp.put("/api/users/profile")
@requiere_token
def editar_perfil():
    datos = cuerpo_json(request)
    usuario = service.editar_perfil(g.id_usuario, datos.get("nombre"), datos.get("email"))
    return jsonify({"message": "Perfil actualizado", "usuario": usuario}), 200


@usuarios_bp.put("/api/auth/change-password")
@requiere_token
def cambiar_password():
    datos = cuerpo_json(request)
    service.cambiar_password(g.id_usuario, datos.get("current_password"), datos.get("new_password"))
    return jsonify({"message": "Contraseña actualizada"}), 200
