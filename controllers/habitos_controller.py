from flask import Blueprint, request, jsonify
from models.habito_model import crear_habito, obtener_habitos_de_usuario
from middleware.auth_middleware import requiere_token

habitos_bp = Blueprint("habitos", __name__)

@habitos_bp.route("/api/habitos/", methods=["GET"])
@requiere_token
def listar_habitos():
    # request.id_usuario lo puso el middleware al validar el token:
    # por eso cada quien ve solo lo suyo, sin poder pedir los de otro
    habitos = obtener_habitos_de_usuario(request.id_usuario)
    return jsonify({"habitos": habitos}), 200

@habitos_bp.route("/api/habitos/", methods=["POST"])
@requiere_token
def registrar_habito():
    data = request.get_json()
    descripcion = data.get("descripcion")
    categoria = data.get("categoria", "General")

    if not descripcion:
        return jsonify({"error": "La descripción es obligatoria"}), 400

    nuevo_id = crear_habito(request.id_usuario, descripcion, categoria)
    return jsonify({"message": "Hábito registrado", "id": nuevo_id}), 201