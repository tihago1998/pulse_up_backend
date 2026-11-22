"""Reglas de negocio del plan semanal, la regla de descanso muscular, la rutina del día y el calendario."""
import calendar
import math
import re
import sqlite3
from datetime import date, timedelta

from flask import current_app

from pulseup.core import tiempo
from pulseup.core.database import conexion
from pulseup.core.dominio import DIAS_SEMANA, GRUPOS_SIN_DESCANSO
from pulseup.core.errors import Conflicto, NoEncontrado, SolicitudInvalida
from pulseup.core.validacion import exigir_fecha
from pulseup.modules.plan import repository as repo
from pulseup.modules.plan.schemas import (
    conflicto_a_json,
    dia_calendario_a_json,
    dia_plan_a_json,
    incumplido_a_json,
    rutina_corta,
)
from pulseup.modules.rutinas import repository as rutinas_repo

CUMPLIDO = "cumplido"
PENDIENTE = "pendiente"
INCUMPLIDO = "incumplido"
DESCANSO = "descanso"

_FORMATO_MES = re.compile(r"^\d{4}-\d{2}$")


# ---- Validaciones de entrada --------------------------------------------------

def _es_entero(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _exigir_dia(valor):
    if not _es_entero(valor) or not 1 <= valor <= 7:
        raise SolicitudInvalida("dia_semana debe ser un número entre 1 (lunes) y 7 (domingo)")
    return valor


def _exigir_id_rutina(valor):
    if not _es_entero(valor) or valor < 1:
        raise SolicitudInvalida("id_rutina es obligatorio y debe ser un número")
    return valor


# ---- Regla de descanso muscular -----------------------------------------------

def dias_minimos_de_descanso():
    """Distancia mínima en días entre dos días que trabajan el mismo grupo (48 h -> 2 días)."""
    return math.ceil(current_app.config["DESCANSO_MUSCULAR_HORAS"] / 24)


def distancia_circular(dia_a, dia_b):
    """Días entre dos días de la semana, contando que domingo (7) y lunes (1) son consecutivos."""
    diferencia = abs(dia_a - dia_b) % 7
    return min(diferencia, 7 - diferencia)


def conflictos_de_descanso(dia_semana, grupos_nuevos, grupos_por_dia):
    """Lista de conflictos de poner `grupos_nuevos` en `dia_semana`.

    `grupos_por_dia` es {dia_semana: grupos} del plan actual. El propio día se ignora:
    al reemplazar su rutina, la anterior deja de contar. Solo cuentan los grupos
    principales y no los exentos (abdomen, pantorrillas, cardio, cuerpo completo).
    """
    minimo = dias_minimos_de_descanso()
    nuevos = set(grupos_nuevos) - set(GRUPOS_SIN_DESCANSO)
    conflictos = []
    # Primero los días más cercanos: son los que dan el mensaje más claro
    otros = sorted(
        (d for d in grupos_por_dia if d != dia_semana),
        key=lambda d: (distancia_circular(dia_semana, d), d),
    )
    for otro_dia in otros:
        if distancia_circular(dia_semana, otro_dia) >= minimo:
            continue
        for grupo in sorted(nuevos & set(grupos_por_dia[otro_dia])):
            conflictos.append(conflicto_a_json(grupo, otro_dia))
    return conflictos


def _mensaje_conflicto(conflictos):
    primero = conflictos[0]
    horas = current_app.config["DESCANSO_MUSCULAR_HORAS"]
    mensaje = (
        f"{primero['grupo'].capitalize()} ya se entrena el {primero['nombre_dia']}; "
        f"necesita {horas} h de descanso antes de volver a trabajarlo"
    )
    if len(conflictos) > 1:
        mensaje += f" (hay {len(conflictos)} conflictos en total)"
    return mensaje


def _evaluar_asignacion(conn, id_usuario, dia_semana, id_rutina):
    """Comprueba que la rutina sea visible y devuelve los conflictos de descanso."""
    if rutinas_repo.buscar_visible(conn, id_rutina, id_usuario) is None:
        raise NoEncontrado("Rutina no encontrada")
    plan = repo.listar(conn, id_usuario)
    grupos = repo.grupos_por_rutina(conn, [id_rutina] + [f["id_rutina"] for f in plan])
    grupos_por_dia = {f["dia_semana"]: grupos[f["id_rutina"]] for f in plan}
    return conflictos_de_descanso(dia_semana, grupos[id_rutina], grupos_por_dia)


# ---- Plan semanal -------------------------------------------------------------

def ver_plan(id_usuario):
    with conexion() as conn:
        plan = {f["dia_semana"]: f for f in repo.listar(conn, id_usuario)}
        grupos = repo.grupos_por_rutina(conn, [f["id_rutina"] for f in plan.values()])
    return [
        dia_plan_a_json(dia, plan.get(dia), grupos.get(plan[dia]["id_rutina"], ()) if dia in plan else ())
        for dia in DIAS_SEMANA
    ]


def asignar(id_usuario, dia_semana, datos):
    _exigir_dia(dia_semana)
    id_rutina = _exigir_id_rutina(datos.get("id_rutina"))
    with conexion() as conn:
        conflictos = _evaluar_asignacion(conn, id_usuario, dia_semana, id_rutina)
        if conflictos:
            raise Conflicto(_mensaje_conflicto(conflictos), extra={"conflictos": conflictos})
        repo.asignar(conn, id_usuario, dia_semana, id_rutina, tiempo.hoy().isoformat())
        fila = repo.buscar_dia(conn, id_usuario, dia_semana)
        grupos = repo.grupos_por_rutina(conn, [id_rutina])[id_rutina]
    return dia_plan_a_json(dia_semana, fila, grupos)


def quitar(id_usuario, dia_semana):
    _exigir_dia(dia_semana)
    with conexion() as conn:
        repo.quitar(conn, id_usuario, dia_semana)
    return dia_plan_a_json(dia_semana)


def validar(id_usuario, datos):
    """Igual que asignar, pero sin guardar nada."""
    dia_semana = _exigir_dia(datos.get("dia_semana"))
    id_rutina = _exigir_id_rutina(datos.get("id_rutina"))
    with conexion() as conn:
        conflictos = _evaluar_asignacion(conn, id_usuario, dia_semana, id_rutina)
    resultado = {"valido": not conflictos, "conflictos": conflictos}
    if conflictos:
        resultado["mensaje"] = _mensaje_conflicto(conflictos)
    return resultado


# ---- Rutina del día -----------------------------------------------------------

def completar(id_usuario, datos):
    """Marca como cumplida la rutina de HOY. El día que se pierde no se recupera."""
    hoy = tiempo.hoy()
    fecha = datos.get("fecha")
    if fecha is not None and fecha != hoy.isoformat():
        raise SolicitudInvalida("Solo puedes marcar la rutina de hoy; los días pasados o futuros no se pueden marcar")

    with conexion() as conn:
        entrada = repo.buscar_dia(conn, id_usuario, hoy.isoweekday())
        # Días anteriores a `creado_en` son descanso; hoy nunca lo es porque creado_en <= hoy
        if entrada is None:
            raise SolicitudInvalida("Hoy es tu día de descanso")
        if "id_rutina" in datos and datos["id_rutina"] != entrada["id_rutina"]:
            raise SolicitudInvalida("Esa no es la rutina planificada para hoy")
        if repo.buscar_sesion(conn, id_usuario, hoy.isoformat()) is not None:
            raise Conflicto("Ya marcaste la rutina de hoy")
        completada_en = tiempo.ahora().isoformat(timespec="seconds")
        try:
            repo.crear_sesion(conn, id_usuario, hoy.isoformat(), entrada["id_rutina"], completada_en)
        except sqlite3.IntegrityError:
            # Dos peticiones casi simultáneas: la restricción UNIQUE decide
            raise Conflicto("Ya marcaste la rutina de hoy")

    return {
        "fecha": hoy.isoformat(),
        "dia_semana": hoy.isoweekday(),
        "nombre_dia": DIAS_SEMANA[hoy.isoweekday()],
        "rutina": rutina_corta(entrada["id_rutina"], entrada["nombre"]),
        "completada_en": completada_en,
    }


# ---- Calendario ---------------------------------------------------------------

def _estado_del_dia(fecha, hoy, plan, fechas_cumplidas):
    """Estado de una fecha según el plan actual y las sesiones registradas."""
    if fecha.isoformat() in fechas_cumplidas:
        return CUMPLIDO
    entrada = plan.get(fecha.isoweekday())
    # Sin rutina ese día, o antes de haberla planificado: no se castiga el pasado
    if entrada is None or fecha.isoformat() < entrada["creado_en"]:
        return DESCANSO
    return PENDIENTE if fecha >= hoy else INCUMPLIDO


def _primer_dia_relevante(plan, fechas_cumplidas):
    fechas = [f["creado_en"] for f in plan.values()] + list(fechas_cumplidas)
    return date.fromisoformat(min(fechas)) if fechas else None


def _racha(hoy, plan, fechas_cumplidas):
    """Días planificados cumplidos seguidos. El descanso no cuenta ni rompe; un incumplido rompe.
    Hoy sin marcar está pendiente: tampoco rompe la racha."""
    dia = _primer_dia_relevante(plan, fechas_cumplidas)
    actual = mejor = 0
    while dia is not None and dia <= hoy:
        estado = _estado_del_dia(dia, hoy, plan, fechas_cumplidas)
        if estado == CUMPLIDO:
            actual += 1
            mejor = max(mejor, actual)
        elif estado == INCUMPLIDO:
            actual = 0
        dia += timedelta(days=1)
    return {"actual": actual, "mejor": mejor}


def _leer_mes(mes, hoy):
    if mes is None:
        return hoy.year, hoy.month
    try:
        if not _FORMATO_MES.match(mes):
            raise ValueError
        anio, numero = int(mes[:4]), int(mes[5:])
        date(anio, numero, 1)
        return anio, numero
    except ValueError:
        raise SolicitudInvalida("Mes inválido, usa el formato YYYY-MM")


def calendario(id_usuario, mes=None):
    hoy = tiempo.hoy()
    anio, numero = _leer_mes(mes, hoy)
    primero = date(anio, numero, 1)
    ultimo = date(anio, numero, calendar.monthrange(anio, numero)[1])

    with conexion() as conn:
        plan = {f["dia_semana"]: f for f in repo.listar(conn, id_usuario)}
        sesiones = {s["fecha"]: s for s in repo.sesiones_entre(conn, id_usuario, primero.isoformat(), ultimo.isoformat())}
        fechas_cumplidas = repo.fechas_con_sesion(conn, id_usuario)

    dias = []
    fecha = primero
    while fecha <= ultimo:
        estado = _estado_del_dia(fecha, hoy, plan, fechas_cumplidas)
        if estado == CUMPLIDO:
            s = sesiones[fecha.isoformat()]
            rutina = rutina_corta(s["id_rutina"], s["nombre"])
        elif estado == DESCANSO:
            rutina = None
        else:
            p = plan[fecha.isoweekday()]
            rutina = rutina_corta(p["id_rutina"], p["nombre"])
        dias.append(dia_calendario_a_json(fecha, estado, rutina))
        fecha += timedelta(days=1)

    return {"mes": f"{anio:04d}-{numero:02d}", "dias": dias, "racha": _racha(hoy, plan, fechas_cumplidas)}


def incumplidos(id_usuario, desde=None):
    """Días pasados con rutina planificada y sin sesión, del más reciente al más antiguo.
    Por defecto solo ayer. Se usará para la notificación de "no cumpliste la rutina del ...".
    """
    hoy = tiempo.hoy()
    ayer = hoy - timedelta(days=1)
    inicio = date.fromisoformat(exigir_fecha(desde)) if desde else ayer

    with conexion() as conn:
        plan = {f["dia_semana"]: f for f in repo.listar(conn, id_usuario)}
        fechas_cumplidas = repo.fechas_con_sesion(conn, id_usuario)

    # Nada antes de la primera planificación puede estar incumplido: se acota el recorrido
    if not plan:
        return []
    inicio = max(inicio, min(date.fromisoformat(f["creado_en"]) for f in plan.values()))

    resultado = []
    fecha = ayer
    while fecha >= inicio:
        if _estado_del_dia(fecha, hoy, plan, fechas_cumplidas) == INCUMPLIDO:
            resultado.append(incumplido_a_json(fecha, plan[fecha.isoweekday()]))
        fecha -= timedelta(days=1)
    return resultado
