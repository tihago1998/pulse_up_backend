"""Rutas HTTP de rutinas."""
from flask import Blueprint, g, jsonify, request

from pulseup.core.auth import requiere_token
from pulseup.core.validacion import cuerpo_json
from pulseup.modules.rutinas import service

rutinas_bp = Blueprint("rutinas", __name__)


@rutinas_bp.get("/api/rutinas/")
@requiere_token
def listar():
    rutinas = service.listar(g.id_usuario, request.args.get("objetivo"), request.args.get("nivel"))
    return jsonify({"rutinas": rutinas}), 200


@rutinas_bp.get("/api/rutinas/<int:id_rutina>")
@requiere_token
def detalle(id_rutina):
    return jsonify({"rutina": service.detalle(id_rutina, g.id_usuario)}), 200


@rutinas_bp.post("/api/rutinas/")
@requiere_token
def crear():
    nuevo_id = service.crear(g.id_usuario, cuerpo_json(request))
    return jsonify({"message": "Rutina creada", "id": nuevo_id}), 201


@rutinas_bp.delete("/api/rutinas/<int:id_rutina>")
@requiere_token
def eliminar(id_rutina):
    service.eliminar(id_rutina, g.id_usuario)
    return jsonify({"message": "Rutina eliminada"}), 200
