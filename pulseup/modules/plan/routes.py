"""Rutas HTTP del plan semanal, la rutina del día y el calendario."""
from flask import Blueprint, g, jsonify, request

from pulseup.core.auth import requiere_token
from pulseup.core.validacion import cuerpo_json
from pulseup.modules.calorias.service import NOTA as NOTA_CALORIAS
from pulseup.modules.plan import ejercicios_service, service

plan_bp = Blueprint("plan", __name__)


@plan_bp.get("/api/plan/")
@requiere_token
def ver():
    return jsonify({"plan": service.ver_plan(g.id_usuario), "calorias_nota": NOTA_CALORIAS}), 200


@plan_bp.put("/api/plan/<int:dia>")
@requiere_token
def asignar(dia):
    # La regla de 48 h no bloquea: si hay choques se guarda igual y vienen en "avisos"
    dia_plan, avisos = service.asignar(g.id_usuario, dia, cuerpo_json(request))
    return jsonify(
        {"message": "Rutina asignada", "dia": dia_plan, "avisos": avisos, "calorias_nota": NOTA_CALORIAS}
    ), 200


@plan_bp.delete("/api/plan/<int:dia>")
@requiere_token
def quitar(dia):
    dia_plan = service.quitar(g.id_usuario, dia)
    return jsonify({"message": "Día marcado como descanso", "dia": dia_plan, "calorias_nota": NOTA_CALORIAS}), 200


# ---- Ejercicios del catálogo en un día del plan ---------------------------------------

@plan_bp.get("/api/plan/previsualizar")
@requiere_token
def previsualizar():
    dias = ejercicios_service.previsualizar(
        g.id_usuario, request.args.get("ejercicio_id"), request.args.get("rutina_id")
    )
    return jsonify({"dias": dias}), 200


@plan_bp.post("/api/plan/<int:dia>/ejercicios")
@requiere_token
def agregar_ejercicio(dia):
    resultado = ejercicios_service.agregar(g.id_usuario, dia, cuerpo_json(request))
    return jsonify({**resultado, "calorias_nota": NOTA_CALORIAS}), 201


@plan_bp.put("/api/plan/<int:dia>/ejercicios/<int:item_id>")
@requiere_token
def editar_ejercicio(dia, item_id):
    resultado = ejercicios_service.editar(g.id_usuario, dia, item_id, cuerpo_json(request))
    return jsonify({**resultado, "calorias_nota": NOTA_CALORIAS}), 200


@plan_bp.delete("/api/plan/<int:dia>/ejercicios/<int:item_id>")
@requiere_token
def quitar_ejercicio(dia, item_id):
    resultado = ejercicios_service.quitar(g.id_usuario, dia, item_id)
    return jsonify({"message": "Ejercicio quitado del día", **resultado, "calorias_nota": NOTA_CALORIAS}), 200


@plan_bp.post("/api/plan/validar")
@requiere_token
def validar():
    return jsonify(service.validar(g.id_usuario, cuerpo_json(request))), 200


@plan_bp.post("/api/plan/completar")
@requiere_token
def completar():
    sesion = service.completar(g.id_usuario, cuerpo_json(request))
    return jsonify({"message": "¡Rutina de hoy cumplida!", "sesion": sesion, "calorias_nota": NOTA_CALORIAS}), 201


@plan_bp.get("/api/plan/incumplidos")
@requiere_token
def incumplidos():
    return jsonify({"incumplidos": service.incumplidos(g.id_usuario, request.args.get("desde"))}), 200


@plan_bp.get("/api/calendario/")
@requiere_token
def calendario():
    return jsonify({**service.calendario(g.id_usuario, request.args.get("mes")), "calorias_nota": NOTA_CALORIAS}), 200
