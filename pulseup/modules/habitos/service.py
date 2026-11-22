"""Reglas de negocio de hábitos."""
from datetime import date

from pulseup.core.database import conexion
from pulseup.core.errors import NoEncontrado, SolicitudInvalida
from pulseup.core.validacion import exigir_fecha
from pulseup.modules.habitos import repository as repo


def listar(id_usuario, fecha=None):
    if fecha:
        exigir_fecha(fecha)
    with conexion() as conn:
        return repo.listar(conn, id_usuario, fecha)


def registrar(id_usuario, descripcion, categoria, fecha):
    descripcion = (descripcion or "").strip()
    if not descripcion:
        raise SolicitudInvalida("La descripción es obligatoria")
    if fecha:
        exigir_fecha(fecha)
    categoria = (categoria or "").strip() or "General"
    # Sin fecha, el hábito es para hoy. Con fecha se pueden programar días futuros.
    with conexion() as conn:
        return repo.crear(conn, id_usuario, descripcion, categoria, fecha or date.today().isoformat())


def cambiar_completado(id_habito, id_usuario, completado):
    with conexion() as conn:
        if not repo.marcar_completado(conn, id_habito, id_usuario, completado):
            raise NoEncontrado("Hábito no encontrado")


def resumen(id_usuario, desde, hasta):
    mensaje = "Usa desde y hasta con formato YYYY-MM-DD"
    exigir_fecha(desde, mensaje)
    exigir_fecha(hasta, mensaje)
    with conexion() as conn:
        return repo.resumen_por_dias(conn, id_usuario, desde, hasta)
