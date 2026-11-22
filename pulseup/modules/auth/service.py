"""Registro e inicio de sesión."""
from pulseup.core import roles as R
from pulseup.core.database import conexion
from pulseup.core.errors import Conflicto, NoAutenticado, SolicitudInvalida
from pulseup.core.security import generar_token, hashear_password, password_correcta
from pulseup.modules.usuarios import repository as usuarios_repo
from pulseup.modules.usuarios.schemas import usuario_a_json


def registrar(nombre, email, password):
    if not nombre or not email or not password:
        raise SolicitudInvalida("Faltan campos requeridos")
    with conexion() as conn:
        if usuarios_repo.buscar_por_email(conn, email):
            raise Conflicto("El correo ya está registrado")
        # Todo usuario nuevo nace con el rol Usuario
        return usuarios_repo.crear(conn, nombre, email, hashear_password(password), R.ID_USUARIO)


def iniciar_sesion(email, password):
    with conexion() as conn:
        usuario = usuarios_repo.buscar_por_email(conn, email) if email else None
        # Mismo mensaje si el correo no existe o la contraseña no coincide (por seguridad)
        if usuario is None or not password or not password_correcta(usuario["password_hash"], password):
            raise NoAutenticado("Correo o contraseña incorrectos")
        roles = usuarios_repo.roles_de_usuario(conn, usuario["id_usuario"])
    token = generar_token(usuario["id_usuario"], roles)
    return token, usuario_a_json(usuario, roles)
