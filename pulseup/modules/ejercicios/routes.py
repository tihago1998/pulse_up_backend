"""Rutas HTTP del catálogo de ejercicios."""
from flask import Blueprint, jsonify, request

from pulseup.core.auth import requiere_token
from pulseup.modules.ejercicios import service

ejercicios_bp = Blueprint("ejercicios", __name__)


@ejercicios_bp.get("/api/ejercicios/")
@requiere_token
def listar():
    a = request.args
    ejercicios = service.listar(a.get("musculo"), a.get("equipo"), a.get("nivel"), a.get("q"))
    return jsonify({"ejercicios": ejercicios}), 200


# Esta ruta va antes que /<id> para que "filtros" no se confunda con un id
@ejercicios_bp.get("/api/ejercicios/filtros")
@requiere_token
def filtros():
    return jsonify(service.filtros()), 200


@ejercicios_bp.get("/api/ejercicios/<int:id_ejercicio>")
@requiere_token
def detalle(id_ejercicio):
    return jsonify({"ejercicio": service.detalle(id_ejercicio)}), 200
