from datetime import datetime
from flask import Blueprint, request, jsonify
from models.habito_model import (
    crear_habito,
    obtener_habitos_de_usuario,
    marcar_completado,
    resumen_por_dias,
)
from middleware.auth_middleware import requiere_token

habitos_bp = Blueprint("habitos", __name__)


def _fecha_valida(texto):
    # Acepta solo YYYY-MM-DD
    try:
        datetime.strptime(texto, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


@habitos_bp.route("/api/habitos/", methods=["GET"])
@requiere_token
def listar_habitos():
    # request.id_usuario lo puso el middleware al validar el token:
    # por eso cada quien ve solo lo suyo, sin poder pedir los de otro
    fecha = request.args.get("fecha")
    if fecha and not _fecha_valida(fecha):
        return jsonify({"error": "Fecha inválida, usa el formato YYYY-MM-DD"}), 400

    habitos = obtener_habitos_de_usuario(request.id_usuario, fecha)
    return jsonify({"habitos": habitos}), 200


@habitos_bp.route("/api/habitos/", methods=["POST"])
@requiere_token
def registrar_habito():
    data = request.get_json(silent=True) or {}
    descripcion = (data.get("descripcion") or "").strip()
    categoria = data.get("categoria", "General")
    fecha = data.get("fecha")

    if not descripcion:
        return jsonify({"error": "La descripción es obligatoria"}), 400
    if fecha and not _fecha_valida(fecha):
        return jsonify({"error": "Fecha inválida, usa el formato YYYY-MM-DD"}), 400

    nuevo_id = crear_habito(request.id_usuario, descripcion, categoria, fecha)
    return jsonify({"message": "Hábito registrado", "id": nuevo_id}), 201


@habitos_bp.route("/api/habitos/<int:id_habito>/completado", methods=["PATCH"])
@requiere_token
def cambiar_completado(id_habito):
    data = request.get_json(silent=True) or {}
    if "completado" not in data:
        return jsonify({"error": "Falta el campo completado"}), 400

    if not marcar_completado(id_habito, request.id_usuario, bool(data["completado"])):
        return jsonify({"error": "Hábito no encontrado"}), 404

    return jsonify({"message": "Hábito actualizado"}), 200


@habitos_bp.route("/api/habitos/resumen", methods=["GET"])
@requiere_token
def resumen():
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    if not (_fecha_valida(desde) and _fecha_valida(hasta)):
        return jsonify({"error": "Usa desde y hasta con formato YYYY-MM-DD"}), 400

    return jsonify({"dias": resumen_por_dias(request.id_usuario, desde, hasta)}), 200