"""Reglas de negocio de rutinas."""
from pulseup.core.database import conexion
from pulseup.core.dominio import NIVELES, OBJETIVOS
from pulseup.core.errors import Conflicto, NoEncontrado, Prohibido, SolicitudInvalida
from pulseup.modules.ejercicios import repository as ejercicios_repo
from pulseup.modules.plan import repository as plan_repo
from pulseup.modules.rutinas import repository as repo
from pulseup.modules.rutinas.schemas import rutina_a_json, rutina_detalle_a_json

MAX_EJERCICIOS = 20


def listar(id_usuario, objetivo=None, nivel=None):
    if objetivo and objetivo not in OBJETIVOS:
        raise SolicitudInvalida("Objetivo no válido. Usa: " + ", ".join(OBJETIVOS))
    if nivel and nivel not in NIVELES:
        raise SolicitudInvalida("Nivel no válido. Usa: " + ", ".join(NIVELES))
    with conexion() as conn:
        return [rutina_a_json(f) for f in repo.listar_visibles(conn, id_usuario, objetivo, nivel)]


def detalle(id_rutina, id_usuario):
    with conexion() as conn:
        fila = repo.buscar_visible(conn, id_rutina, id_usuario)
        if fila is None:
            raise NoEncontrado("Rutina no encontrada")
        return rutina_detalle_a_json(fila, repo.ejercicios_de_rutina(conn, id_rutina))


def _entero(valor, campo, minimo, maximo):
    if isinstance(valor, bool) or not isinstance(valor, int) or not minimo <= valor <= maximo:
        raise SolicitudInvalida(f"{campo} debe ser un número entre {minimo} y {maximo}")
    return valor


def _validar_items(items):
    if not isinstance(items, list) or not items:
        raise SolicitudInvalida("La rutina necesita al menos un ejercicio")
    if len(items) > MAX_EJERCICIOS:
        raise SolicitudInvalida(f"Una rutina admite máximo {MAX_EJERCICIOS} ejercicios")
    limpios = []
    for it in items:
        if not isinstance(it, dict):
            raise SolicitudInvalida("Cada ejercicio debe ser un objeto")
        repeticiones = str(it.get("repeticiones", "")).strip()
        if not repeticiones:
            raise SolicitudInvalida("Cada ejercicio necesita repeticiones (por ejemplo 8-12)")
        limpios.append(
            {
                "id_ejercicio": _entero(it.get("id_ejercicio"), "id_ejercicio", 1, 10**9),
                "series": _entero(it.get("series"), "series", 1, 10),
                "repeticiones": repeticiones[:20],
                "descanso_seg": _entero(it.get("descanso_seg", 60), "descanso_seg", 0, 600),
            }
        )
    return limpios


def crear(id_usuario, datos):
    nombre = (datos.get("nombre") or "").strip()
    if not nombre:
        raise SolicitudInvalida("El nombre es obligatorio")
    objetivo = datos.get("objetivo", "general")
    nivel = datos.get("nivel", "principiante")
    if objetivo not in OBJETIVOS:
        raise SolicitudInvalida("Objetivo no válido. Usa: " + ", ".join(OBJETIVOS))
    if nivel not in NIVELES:
        raise SolicitudInvalida("Nivel no válido. Usa: " + ", ".join(NIVELES))
    duracion = _entero(datos.get("duracion_min", 45), "duracion_min", 5, 240)
    items = _validar_items(datos.get("ejercicios"))

    with conexion() as conn:
        if ejercicios_repo.ids_existentes(conn, {i["id_ejercicio"] for i in items}) != {i["id_ejercicio"] for i in items}:
            raise SolicitudInvalida("Alguno de los ejercicios no existe")
        return repo.crear(
            conn, id_usuario, nombre, (datos.get("descripcion") or "").strip(), objetivo, nivel, duracion, items
        )


def eliminar(id_rutina, id_usuario):
    with conexion() as conn:
        fila = repo.buscar_visible(conn, id_rutina, id_usuario)
        if fila is None:
            raise NoEncontrado("Rutina no encontrada")
        if fila["id_usuario"] is None:
            raise Prohibido("Las rutinas del sistema no se pueden eliminar")
        if plan_repo.rutina_en_algun_plan(conn, id_rutina):
            raise Conflicto("La rutina está en tu plan semanal; quítala del plan antes de eliminarla")
        repo.eliminar(conn, id_rutina)
