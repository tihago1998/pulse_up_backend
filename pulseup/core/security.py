"""Contraseñas y tokens JWT."""
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

HORAS_DE_VIDA_DEL_TOKEN = 24


def hashear_password(password):
    return generate_password_hash(password)


def password_correcta(password_hash, password):
    return check_password_hash(password_hash, password)


def generar_token(id_usuario, roles):
    payload = {
        "id_usuario": id_usuario,
        "roles": roles,
        "exp": datetime.now(timezone.utc) + timedelta(hours=HORAS_DE_VIDA_DEL_TOKEN),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decodificar_token(token):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
