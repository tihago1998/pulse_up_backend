"""Consulta del catálogo de ejercicios."""
from pulseup.core.database import conexion
from pulseup.core.dominio import NIVELES
from pulseup.core.errors import NoEncontrado, SolicitudInvalida
from pulseup.modules.ejercicios import repository as repo
from pulseup.modules.ejercicios.schemas import ejercicio_a_json


def listar(musculo=None, equipo=None, nivel=None, texto=None):
    if nivel and nivel not in NIVELES:
        raise SolicitudInvalida("Nivel no válido. Usa: " + ", ".join(NIVELES))
    with conexion() as conn:
        filas = repo.listar(conn, musculo, equipo, nivel, (texto or "").strip() or None)
        return [ejercicio_a_json(f, con_instrucciones=False) for f in filas]


def detalle(id_ejercicio):
    with conexion() as conn:
        fila = repo.buscar_por_id(conn, id_ejercicio)
        if fila is None:
            raise NoEncontrado("Ejercicio no encontrado")
        return ejercicio_a_json(fila)


def filtros():
    """Valores disponibles para armar los filtros de la pantalla."""
    with conexion() as conn:
        return {
            "musculos": repo.valores_distintos(conn, "grupo_muscular"),
            "equipos": repo.valores_distintos(conn, "equipo"),
            "niveles": list(NIVELES),
        }
