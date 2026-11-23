"""Rutas HTTP del perfil físico del usuario autenticado."""
from flask import Blueprint, g, jsonify, request

from pulseup.core.auth import requiere_token
from pulseup.core.validacion import cuerpo_json
from pulseup.modules.perfil_fisico import service

perfil_fisico_bp = Blueprint("perfil_fisico", __name__)


@perfil_fisico_bp.get("/api/perfil-fisico/")
@requiere_token
def ver():
    return jsonify({"perfil": service.ver(g.id_usuario)}), 200


@perfil_fisico_bp.put("/api/perfil-fisico/")
@requiere_token
def guardar():
    perfil = service.guardar(g.id_usuario, cuerpo_json(request))
    return jsonify({"message": "Perfil guardado", "perfil": perfil}), 200


@perfil_fisico_bp.delete("/api/perfil-fisico/")
@requiere_token
def eliminar():
    service.eliminar(g.id_usuario)
    return jsonify({"message": "Perfil eliminado"}), 200
