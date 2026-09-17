from functools import wraps
# wraps mantiene el nombre y la información original de la función que decoramos,
# evitando problemas al usar varios decoradores juntos
from flask import request, jsonify
import jwt
from config import SECRET_KEY

def requiere_token(f):
    # Este decorador se coloca sobre cualquier ruta que requiera que el usuario
    # esté autenticado (haya hecho login previamente)
    @wraps(f)
    def decorador(*args, **kwargs):
        # Buscamos el encabezado "Authorization" en la petición HTTP
        auth_header = request.headers.get("Authorization", "")

        # Debe venir en formato "Bearer <token>"
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token no proporcionado"}), 401

        # Extraemos solo el token, quitando la palabra "Bearer "
        token = auth_header.replace("Bearer ", "")

        try:
            # Verificamos que el token sea válido y no haya sido alterado
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        # Guardamos los datos del usuario dentro del objeto "request" de Flask,
        # así la función de la ruta (y otros decoradores) pueden usarlos después
        request.id_usuario = payload["id_usuario"]
        request.roles = payload["roles"]

        # Si todo salió bien, dejamos que la función original se ejecute
        return f(*args, **kwargs)
    return decorador

def requiere_admin(f):
    # Este decorador se usa JUNTO a @requiere_token, en las rutas que solo
    # puede usar un Administrador. Esta es la "segunda capa de seguridad"
    # que menciona la guía: aunque alguien llame el endpoint directamente
    # con Postman, si no tiene el rol correcto, el servidor lo rechaza.
    @wraps(f)
    def decorador(*args, **kwargs):
        if "Administrador" not in getattr(request, "roles", []):
            return jsonify({"error": "Acceso prohibido: se requiere rol Administrador"}), 403
        return f(*args, **kwargs)
    return decorador

def requiere_admin_o_superadmin(f):
    # Deja pasar a cualquiera de los dos roles con privilegios
    @wraps(f)
    def decorador(*args, **kwargs):
        roles = getattr(request, "roles", [])
        if "Administrador" not in roles and "SuperAdministrador" not in roles:
            return jsonify({"error": "Acceso prohibido: se requiere rol Administrador o SuperAdministrador"}), 403
        return f(*args, **kwargs)
    return decorador

def requiere_superadmin(f):
    # Solo el nivel más alto pasa por aquí
    @wraps(f)
    def decorador(*args, **kwargs):
        if "SuperAdministrador" not in getattr(request, "roles", []):
            return jsonify({"error": "Acceso prohibido: se requiere rol SuperAdministrador"}), 403
        return f(*args, **kwargs)
    return decorador