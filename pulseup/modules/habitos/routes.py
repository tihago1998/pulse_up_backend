"""Rutas HTTP de hábitos."""
from flask import Blueprint, g, jsonify, request

from pulseup.core.auth import requiere_token
from pulseup.core.errors import SolicitudInvalida
from pulseup.core.validacion import cuerpo_json
from pulseup.modules.habitos import service

habitos_bp = Blueprint("habitos", __name__)


@habitos_bp.get("/api/habitos/")
@requiere_token
def listar():
    return jsonify({"habitos": service.listar(g.id_usuario, request.args.get("fecha"))}), 200


@habitos_bp.post("/api/habitos/")
@requiere_token
def registrar():
    datos = cuerpo_json(request)
    nuevo_id = service.registrar(g.id_usuario, datos.get("descripcion"), datos.get("categoria"), datos.get("fecha"))
    return jsonify({"message": "Hábito registrado", "id": nuevo_id}), 201


@habitos_bp.patch("/api/habitos/<int:id_habito>/completado")
@requiere_token
def cambiar_completado(id_habito):
    datos = cuerpo_json(request)
    if "completado" not in datos:
        raise SolicitudInvalida("Falta el campo completado")
    service.cambiar_completado(id_habito, g.id_usuario, bool(datos["completado"]))
    return jsonify({"message": "Hábito actualizado"}), 200


@habitos_bp.get("/api/habitos/resumen")
@requiere_token
def resumen():
    dias = service.resumen(g.id_usuario, request.args.get("desde"), request.args.get("hasta"))
    return jsonify({"dias": dias}), 200
