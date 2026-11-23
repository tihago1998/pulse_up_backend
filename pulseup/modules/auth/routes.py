"""Rutas HTTP de registro e inicio de sesión."""
from flask import Blueprint, jsonify, request

from pulseup.core.validacion import cuerpo_json
from pulseup.modules.auth import service

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/api/auth/register")
def register():
    datos = cuerpo_json(request)
    id_usuario = service.registrar(datos.get("nombre"), datos.get("email"), datos.get("password"))
    return jsonify({"message": "Usuario registrado", "id_usuario": id_usuario}), 201


@auth_bp.post("/api/auth/login")
def login():
    datos = cuerpo_json(request)
    token, usuario = service.iniciar_sesion(datos.get("email"), datos.get("password"))
    return jsonify({"token": token, "usuario": usuario}), 200
