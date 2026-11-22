"""Decoradores de acceso. Validan el token y los roles antes de llegar a la ruta."""
from functools import wraps

import jwt
from flask import g, request

from pulseup.core import roles as R
from pulseup.core.errors import NoAutenticado, Prohibido
from pulseup.core.security import decodificar_token


def requiere_token(f):
    """La ruta solo la usa quien haya iniciado sesión. Deja `g.id_usuario` y `g.roles`."""

    @wraps(f)
    def decorador(*args, **kwargs):
        cabecera = request.headers.get("Authorization", "")
        if not cabecera.startswith("Bearer "):
            raise NoAutenticado("Token no proporcionado")
        try:
            payload = decodificar_token(cabecera.removeprefix("Bearer "))
        except jwt.ExpiredSignatureError:
            raise NoAutenticado("Token expirado")
        except jwt.InvalidTokenError:
            raise NoAutenticado("Token inválido")
        g.id_usuario = payload["id_usuario"]
        g.roles = payload["roles"]
        return f(*args, **kwargs)

    return decorador


def requiere_roles(*permitidos, mensaje):
    """Segunda capa de seguridad: aunque llamen al endpoint directo, el servidor valida el rol."""

    def decorar(f):
        @wraps(f)
        def decorador(*args, **kwargs):
            if not set(permitidos) & set(getattr(g, "roles", [])):
                raise Prohibido(mensaje)
            return f(*args, **kwargs)

        return decorador

    return decorar


requiere_admin_o_superadmin = requiere_roles(
    R.ADMINISTRADOR,
    R.SUPERADMINISTRADOR,
    mensaje="Acceso prohibido: se requiere rol Administrador o SuperAdministrador",
)

requiere_superadmin = requiere_roles(
    R.SUPERADMINISTRADOR,
    mensaje="Acceso prohibido: se requiere rol SuperAdministrador",
)
