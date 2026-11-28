"""Rutas HTTP del catálogo de ejercicios."""
from flask import Blueprint, g, jsonify, request

from pulseup.core.auth import requiere_token
from pulseup.modules.ejercicios import service

ejercicios_bp = Blueprint("ejercicios", __name__)


@ejercicios_bp.get("/api/ejercicios/")
@requiere_token
def listar():
    a = request.args
    respuesta = service.listar(
        musculo=a.get("musculo"),
        equipo=a.get("equipo"),
        nivel=a.get("nivel"),
        texto=a.get("q"),
        ambiente=a.get("ambiente"),
        limit=a.get("limit"),
        offset=a.get("offset"),
        formato=a.get("formato"),
        id_usuario=g.id_usuario,
    )
    return jsonify(respuesta), 200


# Estas rutas van antes que /<id> para que "filtros" y "creditos" no se confundan con un id
@ejercicios_bp.get("/api/ejercicios/filtros")
@requiere_token
def filtros():
    return jsonify(service.filtros()), 200


@ejercicios_bp.get("/api/ejercicios/creditos")
@requiere_token
def creditos():
    return jsonify(service.creditos()), 200


@ejercicios_bp.get("/api/ejercicios/<int:id_ejercicio>")
@requiere_token
def detalle(id_ejercicio):
    return jsonify({"ejercicio": service.detalle(id_ejercicio, g.id_usuario)}), 200
