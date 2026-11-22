"""Reglas de negocio de usuarios, perfil y roles."""
from pulseup.core import roles as R
from pulseup.core.database import conexion
from pulseup.core.errors import Conflicto, NoEncontrado, Prohibido, SolicitudInvalida
from pulseup.core.security import hashear_password, password_correcta
from pulseup.modules.habitos import repository as habitos_repo
from pulseup.modules.plan import repository as plan_repo
from pulseup.modules.rutinas import repository as rutinas_repo
from pulseup.modules.usuarios import repository as repo
from pulseup.modules.usuarios.schemas import usuario_a_json


def listar_usuarios():
    with conexion() as conn:
        roles = repo.roles_de_todos(conn)
        return [usuario_a_json(u, roles.get(u["id_usuario"], [])) for u in repo.listar(conn)]


def estadisticas():
    with conexion() as conn:
        return repo.estadisticas(conn)


def asignar_roles(roles_solicitante, id_objetivo, role_ids):
    if not isinstance(role_ids, list) or not all(isinstance(r, int) and not isinstance(r, bool) for r in role_ids):
        raise SolicitudInvalida("role_ids debe ser una lista de números")

    with conexion() as conn:
        if repo.buscar_por_id(conn, id_objetivo) is None:
            raise NoEncontrado("Usuario no encontrado")
        if not set(role_ids) <= repo.ids_de_roles_existentes(conn):
            raise SolicitudInvalida("Alguno de los roles no existe")

        # No basta con ser "algún tipo de admin": importa a QUIÉN se le cambia el rol
        if R.SUPERADMINISTRADOR not in roles_solicitante:
            roles_objetivo = repo.roles_de_usuario(conn, id_objetivo)
            if R.ADMINISTRADOR in roles_objetivo or R.SUPERADMINISTRADOR in roles_objetivo:
                raise Prohibido("Solo un SuperAdministrador puede modificar este rol")
            if R.ID_SUPERADMINISTRADOR in role_ids:
                raise Prohibido("No tienes permisos para asignar ese rol")

        repo.reemplazar_roles(conn, id_objetivo, role_ids)


def eliminar_usuario(id_solicitante, id_objetivo):
    if id_objetivo == id_solicitante:
        raise SolicitudInvalida("No puedes eliminar tu propia cuenta")
    with conexion() as conn:
        # Se limpian también los datos del usuario para no dejar registros huérfanos
        habitos_repo.eliminar_de_usuario(conn, id_objetivo)
        plan_repo.eliminar_de_usuario(conn, id_objetivo)  # antes que las rutinas que referencia
        rutinas_repo.eliminar_de_usuario(conn, id_objetivo)
        repo.eliminar(conn, id_objetivo)


def ver_perfil(id_usuario):
    with conexion() as conn:
        usuario = repo.buscar_por_id(conn, id_usuario)
        if usuario is None:
            raise NoEncontrado("Usuario no encontrado")
        return usuario_a_json(usuario, repo.roles_de_usuario(conn, id_usuario))


def editar_perfil(id_usuario, nombre, email):
    if not nombre or not email:
        raise SolicitudInvalida("Nombre y correo son obligatorios")
    with conexion() as conn:
        if repo.email_usado_por_otro(conn, email, id_usuario):
            raise Conflicto("Ese correo ya está en uso")
        repo.actualizar_perfil(conn, id_usuario, nombre, email)
        usuario = repo.buscar_por_id(conn, id_usuario)
        return usuario_a_json(usuario, repo.roles_de_usuario(conn, id_usuario))


def cambiar_password(id_usuario, actual, nueva):
    if not actual or not nueva:
        raise SolicitudInvalida("Faltan campos requeridos")
    with conexion() as conn:
        usuario = repo.buscar_por_id(conn, id_usuario)
        if usuario is None or not password_correcta(usuario["password_hash"], actual):
            raise SolicitudInvalida("La contraseña actual es incorrecta")
        repo.actualizar_password_hash(conn, id_usuario, hashear_password(nueva))
