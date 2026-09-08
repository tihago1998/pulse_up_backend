from flask import Blueprint, request, jsonify
from auth import registrar_usuario, login_usuario

# Un Blueprint agrupa rutas relacionadas; luego lo "registramos" en app.py
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    # Obtenemos el cuerpo (body) de la petición, que llega en formato JSON
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    # Validación básica: que no falte ningún campo obligatorio
    if not nombre or not email or not password:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    id_usuario, error = registrar_usuario(nombre, email, password)

    if error:
        # 409 = Conflict, código estándar cuando el recurso ya existe (el email)
        return jsonify({"error": error}), 409

    # 201 = Created, código estándar cuando se crea un recurso nuevo exitosamente
    return jsonify({"message": "Usuario registrado", "id_usuario": id_usuario}), 201

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    resultado, error = login_usuario(email, password)

    if error:
        # 401 = Unauthorized, código estándar cuando las credenciales son incorrectas
        return jsonify({"error": error}), 401

    # 200 = OK, todo salió bien; devolvemos el token y los datos del usuario
    return jsonify(resultado), 200