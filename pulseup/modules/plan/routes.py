"""Rutas HTTP del plan semanal, la rutina del día y el calendario."""
from flask import Blueprint, g, jsonify, request

from pulseup.core.auth import requiere_token
from pulseup.core.validacion import cuerpo_json
from pulseup.modules.plan import service

plan_bp = Blueprint("plan", __name__)


@plan_bp.get("/api/plan/")
@requiere_token
def ver():
    return jsonify({"plan": service.ver_plan(g.id_usuario)}), 200


@plan_bp.put("/api/plan/<int:dia>")
@requiere_token
def asignar(dia):
    dia_plan = service.asignar(g.id_usuario, dia, cuerpo_json(request))
    return jsonify({"message": "Rutina asignada", "dia": dia_plan}), 200


@plan_bp.delete("/api/plan/<int:dia>")
@requiere_token
def quitar(dia):
    dia_plan = service.quitar(g.id_usuario, dia)
    return jsonify({"message": "Día marcado como descanso", "dia": dia_plan}), 200


@plan_bp.post("/api/plan/validar")
@requiere_token
def validar():
    return jsonify(service.validar(g.id_usuario, cuerpo_json(request))), 200


@plan_bp.post("/api/plan/completar")
@requiere_token
def completar():
    sesion = service.completar(g.id_usuario, cuerpo_json(request))
    return jsonify({"message": "¡Rutina de hoy cumplida!", "sesion": sesion}), 201


@plan_bp.get("/api/plan/incumplidos")
@requiere_token
def incumplidos():
    return jsonify({"incumplidos": service.incumplidos(g.id_usuario, request.args.get("desde"))}), 200


@plan_bp.get("/api/calendario/")
@requiere_token
def calendario():
    return jsonify(service.calendario(g.id_usuario, request.args.get("mes"))), 200
