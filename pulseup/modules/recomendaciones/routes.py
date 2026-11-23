"""Rutas HTTP de recomendaciones."""
from flask import Blueprint, g, jsonify

from pulseup.core.auth import requiere_token
from pulseup.modules.recomendaciones import service

recomendaciones_bp = Blueprint("recomendaciones", __name__)


# Misma recomendación que trae el detalle del ejercicio, para usarla al armar rutinas
@recomendaciones_bp.get("/api/ejercicios/<int:id_ejercicio>/recomendacion")
@requiere_token
def recomendacion(id_ejercicio):
    return jsonify(service.obtener(id_ejercicio, g.id_usuario)), 200
