"""Reglas de negocio del plan semanal, la regla de descanso muscular (solo avisa), la rutina del día y el calendario."""
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
    aviso_a_json,
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


def conflictos_entre_dias(dia_semana, grupos_nuevos, grupos_por_dia, dias_minimos):
    """Función pura de la regla de descanso: conflictos de poner `grupos_nuevos` en `dia_semana`.

    `grupos_por_dia` es {dia_semana: grupos} del plan actual. El propio día se ignora: al
    reemplazar su rutina la anterior deja de contar, y varios ejercicios del mismo músculo en el
    mismo día no son conflicto (la regla mide la distancia ENTRE días). Solo cuentan los grupos
    principales y no los exentos (abdomen, pantorrillas, cardio, cuerpo completo).
    """
    nuevos = set(grupos_nuevos) - set(GRUPOS_SIN_DESCANSO)
    conflictos = []
    # Primero los días más cercanos: son los que dan el mensaje más claro
    otros = sorted(
        (d for d in grupos_por_dia if d != dia_semana),
        key=lambda d: (distancia_circular(dia_semana, d), d),
    )
    for otro_dia in otros:
        if distancia_circular(dia_semana, otro_dia) >= dias_minimos:
            continue
        for grupo in sorted(nuevos & set(grupos_por_dia[otro_dia])):
            conflictos.append(conflicto_a_json(grupo, otro_dia))
    return conflictos


def conflictos_de_descanso(dia_semana, grupos_nuevos, grupos_por_dia):
    """La regla con las horas de descanso configuradas (DESCANSO_MUSCULAR_HORAS)."""
    return conflictos_entre_dias(dia_semana, grupos_nuevos, grupos_por_dia, dias_minimos_de_descanso())


# Nombres con tilde para los mensajes (los grupos se guardan sin tilde) y grupos en plural
_NOMBRE_MUSCULO = {"cuadriceps": "cuádriceps", "biceps": "bíceps", "triceps": "tríceps", "gluteos": "glúteos"}
_MUSCULOS_EN_PLURAL = ("hombros", "gluteos", "isquiotibiales", "pantorrillas")


def mensaje_aviso(grupo, nombre_dia, horas):
    """Mensaje claro para la app: "El martes ya trabajas pecho: tu pecho necesita 48 horas de descanso"."""
    nombre = _NOMBRE_MUSCULO.get(grupo, grupo)
    if grupo in _MUSCULOS_EN_PLURAL:
        return f"El {nombre_dia} ya trabajas {nombre}: tus {nombre} necesitan {horas} horas de descanso"
    return f"El {nombre_dia} ya trabajas {nombre}: tu {nombre} necesita {horas} horas de descanso"


def avisos_desde_conflictos(conflictos, horas):
    """Función pura: convierte los conflictos de la regla en avisos para la app (no bloquean)."""
    return [
        aviso_a_json(c["grupo"], c["dia_semana"], mensaje_aviso(c["grupo"], c["nombre_dia"], horas))
        for c in conflictos
    ]


def avisos_de_descanso(dia_semana, grupos_nuevos, grupos_por_dia):
    conflictos = conflictos_de_descanso(dia_semana, grupos_nuevos, grupos_por_dia)
    return avisos_desde_conflictos(conflictos, current_app.config["DESCANSO_MUSCULAR_HORAS"])


def grupos_del_plan(conn, id_usuario, ids_extra=()):
    """({dia_semana: grupos} del plan actual, {id_rutina: grupos} incluyendo `ids_extra`)."""
    plan = repo.listar(conn, id_usuario)
    grupos = repo.grupos_por_rutina(conn, list(ids_extra) + [f["id_rutina"] for f in plan])
    return {f["dia_semana"]: grupos[f["id_rutina"]] for f in plan}, grupos


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
    """Comprueba que la rutina sea visible. Devuelve (rutina, conflictos de descanso)."""
    rutina = rutinas_repo.buscar_visible(conn, id_rutina, id_usuario)
    if rutina is None:
        raise NoEncontrado("Rutina no encontrada")
    grupos_por_dia, grupos = grupos_del_plan(conn, id_usuario, [id_rutina])
    return rutina, conflictos_de_descanso(dia_semana, grupos[id_rutina], grupos_por_dia)


# ---- Plan semanal -------------------------------------------------------------

def ver_plan(id_usuario):
    with conexion() as conn:
        plan = {f["dia_semana"]: f for f in repo.listar(conn, id_usuario)}
        ids = [f["id_rutina"] for f in plan.values()]
        grupos = repo.grupos_por_rutina(conn, ids)
        ejercicios = rutinas_repo.items_de_rutinas(conn, ids)
    return [
        dia_plan_a_json(dia, plan[dia], grupos[plan[dia]["id_rutina"]], ejercicios[plan[dia]["id_rutina"]])
        if dia in plan
        else dia_plan_a_json(dia)
        for dia in DIAS_SEMANA
    ]


def dia_a_json(conn, id_usuario, dia_semana):
    """El día del plan tal como lo devuelve GET /api/plan/ (dentro de una conexión abierta)."""
    fila = repo.buscar_dia(conn, id_usuario, dia_semana)
    if fila is None:
        return dia_plan_a_json(dia_semana)
    id_rutina = fila["id_rutina"]
    return dia_plan_a_json(
        dia_semana,
        fila,
        repo.grupos_por_rutina(conn, [id_rutina])[id_rutina],
        rutinas_repo.items_de_rutinas(conn, [id_rutina])[id_rutina],
    )


def asignar_rutina(conn, id_usuario, dia_semana, id_rutina, nombre_rutina, hoy):
    """Pone la rutina en el día respetando el historial. Lo usan PUT /api/plan/<dia> y los
    ejercicios agregados directamente a un día (plan/ejercicios_service.py)."""
    actual = repo.buscar_dia(conn, id_usuario, dia_semana)
    if actual is None or actual["id_rutina"] != id_rutina:
        # El cambio aplica desde hoy: los días anteriores conservan la rutina que tenían
        repo.cerrar_vigencia(conn, id_usuario, dia_semana, hoy)
        repo.abrir_vigencia(conn, id_usuario, dia_semana, id_rutina, nombre_rutina, hoy)
    repo.asignar(conn, id_usuario, dia_semana, id_rutina, hoy)


def quitar_dia(conn, id_usuario, dia_semana, hoy):
    """Deja el día en descanso desde hoy; los días pasados siguen evaluándose con su rutina."""
    repo.cerrar_vigencia(conn, id_usuario, dia_semana, hoy)
    repo.quitar(conn, id_usuario, dia_semana)


def asignar(id_usuario, dia_semana, datos):
    """Asigna la rutina al día. La regla de 48 h solo AVISA: siempre se guarda. Devuelve (día, avisos)."""
    _exigir_dia(dia_semana)
    id_rutina = _exigir_id_rutina(datos.get("id_rutina"))
    hoy = tiempo.hoy().isoformat()
    with conexion() as conn:
        rutina, conflictos = _evaluar_asignacion(conn, id_usuario, dia_semana, id_rutina)
        asignar_rutina(conn, id_usuario, dia_semana, id_rutina, rutina["nombre"], hoy)
        dia = dia_a_json(conn, id_usuario, dia_semana)
    return dia, avisos_desde_conflictos(conflictos, current_app.config["DESCANSO_MUSCULAR_HORAS"])


def quitar(id_usuario, dia_semana):
    _exigir_dia(dia_semana)
    with conexion() as conn:
        quitar_dia(conn, id_usuario, dia_semana, tiempo.hoy().isoformat())
    return dia_plan_a_json(dia_semana)


def validar(id_usuario, datos):
    """Igual que asignar, pero sin guardar nada."""
    dia_semana = _exigir_dia(datos.get("dia_semana"))
    id_rutina = _exigir_id_rutina(datos.get("id_rutina"))
    with conexion() as conn:
        _, conflictos = _evaluar_asignacion(conn, id_usuario, dia_semana, id_rutina)
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
        # Se usa el plan actual: es justo la vigencia abierta del historial que cubre hoy
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
# El pasado se evalúa con el historial del plan (la rutina vigente EN cada fecha), no con el
# plan actual: cambiar o quitar un día del plan no borra los incumplidos que ya ocurrieron.

def _historial_por_dia(filas):
    """{dia_semana: [vigencias]} para buscar rápido la rutina de una fecha."""
    resultado = {}
    for f in filas:
        resultado.setdefault(f["dia_semana"], []).append(f)
    return resultado


def _vigencia(historial, fecha):
    """La vigencia del plan que cubría esa fecha, o None si ese día era descanso."""
    iso = fecha.isoformat()
    for v in historial.get(fecha.isoweekday(), ()):
        if v["vigente_desde"] <= iso and (v["vigente_hasta"] is None or iso < v["vigente_hasta"]):
            return v
    return None


def _estado_del_dia(fecha, hoy, historial, fechas_cumplidas):
    """Estado de una fecha según la rutina planificada para esa fecha y las sesiones registradas."""
    if fecha.isoformat() in fechas_cumplidas:
        return CUMPLIDO
    # Sin rutina ese día, o antes de haberla planificado: no se castiga el pasado
    if _vigencia(historial, fecha) is None:
        return DESCANSO
    return PENDIENTE if fecha >= hoy else INCUMPLIDO


def _primer_dia_relevante(historial, fechas_cumplidas):
    fechas = [v["vigente_desde"] for vs in historial.values() for v in vs] + list(fechas_cumplidas)
    return date.fromisoformat(min(fechas)) if fechas else None


def _racha(hoy, historial, fechas_cumplidas):
    """Días planificados cumplidos seguidos. El descanso no cuenta ni rompe; un incumplido rompe.
    Hoy sin marcar está pendiente: tampoco rompe la racha."""
    dia = _primer_dia_relevante(historial, fechas_cumplidas)
    actual = mejor = 0
    while dia is not None and dia <= hoy:
        estado = _estado_del_dia(dia, hoy, historial, fechas_cumplidas)
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


def _rutina_del_dia(estado, sesion, vigencia):
    if estado == DESCANSO:
        return None
    if estado == CUMPLIDO:
        nombre = sesion["nombre"]
        # Si la rutina ya se eliminó, se usa el nombre guardado en el historial
        if nombre is None and vigencia is not None and vigencia["id_rutina"] == sesion["id_rutina"]:
            nombre = vigencia["nombre_rutina"]
        return rutina_corta(sesion["id_rutina"], nombre)
    return rutina_corta(vigencia["id_rutina"], vigencia["nombre_rutina"])


def calendario(id_usuario, mes=None):
    hoy = tiempo.hoy()
    anio, numero = _leer_mes(mes, hoy)
    primero = date(anio, numero, 1)
    ultimo = date(anio, numero, calendar.monthrange(anio, numero)[1])

    with conexion() as conn:
        historial = _historial_por_dia(repo.historial(conn, id_usuario))
        sesiones = {s["fecha"]: s for s in repo.sesiones_entre(conn, id_usuario, primero.isoformat(), ultimo.isoformat())}
        fechas_cumplidas = repo.fechas_con_sesion(conn, id_usuario)

    dias = []
    fecha = primero
    while fecha <= ultimo:
        estado = _estado_del_dia(fecha, hoy, historial, fechas_cumplidas)
        rutina = _rutina_del_dia(estado, sesiones.get(fecha.isoformat()), _vigencia(historial, fecha))
        dias.append(dia_calendario_a_json(fecha, estado, rutina))
        fecha += timedelta(days=1)

    return {"mes": f"{anio:04d}-{numero:02d}", "dias": dias, "racha": _racha(hoy, historial, fechas_cumplidas)}


def incumplidos(id_usuario, desde=None):
    """Días pasados con rutina planificada y sin sesión, del más reciente al más antiguo.
    Por defecto solo ayer. Se usará para la notificación de "no cumpliste la rutina del ...".
    """
    hoy = tiempo.hoy()
    ayer = hoy - timedelta(days=1)
    inicio = date.fromisoformat(exigir_fecha(desde)) if desde else ayer

    with conexion() as conn:
        historial = _historial_por_dia(repo.historial(conn, id_usuario))
        fechas_cumplidas = repo.fechas_con_sesion(conn, id_usuario)

    # Nada antes de la primera planificación puede estar incumplido: se acota el recorrido
    primero = _primer_dia_relevante(historial, ())
    if primero is None:
        return []
    inicio = max(inicio, primero)

    resultado = []
    fecha = ayer
    while fecha >= inicio:
        if _estado_del_dia(fecha, hoy, historial, fechas_cumplidas) == INCUMPLIDO:
            resultado.append(incumplido_a_json(fecha, _vigencia(historial, fecha)))
        fecha -= timedelta(days=1)
    return resultado
