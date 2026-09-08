from flask import Blueprint, request, jsonify
from models.usuario_model import buscar_por_email, crear_usuario, verificar_password
from models.rol_model import obtener_roles_de_usuario
from utils.jwt_helper import generar_token
from views.usuario_view import usuario_a_json

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

    # Verificamos que el correo no exista ya
    if buscar_por_email(email):
        # 409 = Conflict, código estándar cuando el recurso ya existe (el email)
        return jsonify({"error": "El correo ya está registrado"}), 409

    id_usuario = crear_usuario(nombre, email, password)

    # 201 = Created, código estándar cuando se crea un recurso nuevo exitosamente
    return jsonify({"message": "Usuario registrado", "id_usuario": id_usuario}), 201

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    usuario = buscar_por_email(email)

    # Si no existe el usuario, O la contraseña no coincide, mismo mensaje genérico (por seguridad)
    if not usuario or not verificar_password(usuario, password):
        # 401 = Unauthorized, código estándar cuando las credenciales son incorrectas
        return jsonify({"error": "Correo o contraseña incorrectos"}), 401

    roles = obtener_roles_de_usuario(usuario["id_usuario"])
    token = generar_token(usuario["id_usuario"], roles)

    # 200 = OK, todo salió bien; devolvemos el token y los datos del usuario
    return jsonify({
        "token": token,
        "usuario": usuario_a_json(dict(usuario), roles)
    }), 200