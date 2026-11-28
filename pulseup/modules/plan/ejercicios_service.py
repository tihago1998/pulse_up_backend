"""Ejercicios del catálogo agregados directamente a un día del plan semanal.

Detrás sigue el modelo plan -> rutina -> ejercicios: cada día apunta a una rutina. Al agregar,
editar o quitar un ejercicio de un día:
- Si el día no tiene rutina se crea una rutina del usuario con origen 'plan' ("Lunes · pecho") y se
  asigna con el mismo servicio que PUT /api/plan/<dia> (así se respeta el historial del plan).
- Si la rutina del día es una plantilla, una rutina creada por el usuario en su pantalla de rutinas
  (origen distinto de 'plan') o está asignada también a otros días, se edita una COPIA solo para
  este día (copia al escribir) y se devuelve rutina_copiada = true. Los demás días no cambian.
- La regla de descanso de 48 h solo devuelve avisos; nunca impide guardar.
"""
from pulseup.core import tiempo
from pulseup.core.database import conexion
from pulseup.core.dominio import DIAS_SEMANA, ORIGEN_PLAN
from pulseup.core.errors import Conflicto, NoEncontrado, SolicitudInvalida
from pulseup.modules.ejercicios import repository as ejercicios_repo
from pulseup.modules.plan import repository as repo
from pulseup.modules.plan import service as plan_service
from pulseup.modules.plan.schemas import item_a_json
from pulseup.modules.recomendaciones import service as recomendaciones
from pulseup.modules.rutinas import repository as rutinas_repo
from pulseup.modules.rutinas import service as rutinas_service

# Sin recomendación personalizada (sin perfil físico o ejercicio sin reglas)
POR_DEFECTO = recomendaciones.POR_DEFECTO
CAMPOS_EDITABLES = ("series", "repeticiones", "peso_kg", "unidad", "descanso_seg")
_VALIDADORES = {
    "series": rutinas_service.validar_series,
    "repeticiones": rutinas_service.validar_repeticiones,
    "peso_kg": rutinas_service.validar_peso_kg,
    "unidad": rutinas_service.validar_unidad,
    "descanso_seg": rutinas_service.validar_descanso,
}
SEPARADOR_NOMBRE = " · "
UNIDADES_DE_DURACION = recomendaciones.UNIDADES_DE_DURACION
PASO_DURACION = recomendaciones.PASO_DURACION


# ---- Funciones puras ------------------------------------------------------------------

def redondear_a_multiplo(valor, paso):
    return recomendaciones.redondear_a_multiplo(valor, paso)


def valores_por_defecto(recomendacion):
    """Series, repeticiones, unidad, descanso y peso a partir de la recomendación personalizada.
    Es el mismo cálculo que muestra el listado de ejercicios (recomendaciones.valores_sugeridos)."""
    return recomendaciones.valores_sugeridos(recomendacion)


def campos_validados(datos, exigir_alguno):
    """Solo los campos editables presentes en `datos`, ya validados (peso_kg puede venir null)."""
    cambios = {campo: _VALIDADORES[campo](datos[campo]) for campo in CAMPOS_EDITABLES if campo in datos}
    if exigir_alguno and not cambios:
        raise SolicitudInvalida("Envía al menos uno de: " + ", ".join(CAMPOS_EDITABLES))
    return cambios


def nombre_rutina_para_dia(dia_semana, base):
    return f"{DIAS_SEMANA[dia_semana].capitalize()}{SEPARADOR_NOMBRE}{base}"


def base_del_nombre(nombre, origen):
    """Lo que va tras "<Día> · " en el nombre de una copia ("Lunes · pecho" -> "pecho")."""
    if origen == ORIGEN_PLAN and SEPARADOR_NOMBRE in nombre:
        return nombre.split(SEPARADOR_NOMBRE, 1)[1]
    return nombre


def necesita_copia(rutina, id_usuario, dia_semana, dias_con_la_rutina):
    """Solo se edita en su sitio una rutina propia, creada por el plan y usada únicamente en este día."""
    return (
        rutina["id_usuario"] != id_usuario
        or rutina["origen"] != ORIGEN_PLAN
        or any(d != dia_semana for d in dias_con_la_rutina)
    )


# ---- Validaciones de entrada ----------------------------------------------------------

def _exigir_dia(dia_semana):
    # Coherente con el resto del plan: 1 = lunes ... 7 = domingo
    if not 1 <= dia_semana <= 7:
        raise NoEncontrado("Día no encontrado: usa un número entre 1 (lunes) y 7 (domingo)")


def _exigir_id(valor, campo):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
        raise SolicitudInvalida(f"{campo} es obligatorio y debe ser un número")
    return valor


def _id_de_query(texto, campo):
    try:
        return _exigir_id(int(texto), campo)
    except (TypeError, ValueError):
        raise SolicitudInvalida(f"{campo} debe ser un número")


# ---- Rutina del día -------------------------------------------------------------------

def _rutina_para_editar(conn, id_usuario, dia_semana, entrada, hoy):
    """(id de la rutina que se puede modificar para este día, rutina_copiada)."""
    rutina = rutinas_repo.buscar_visible(conn, entrada["id_rutina"], id_usuario)
    if rutina is None:  # nunca se toca una rutina de otro usuario
        raise NoEncontrado("Rutina no encontrada")
    dias = repo.dias_con_rutina(conn, id_usuario, rutina["id"])
    if not necesita_copia(rutina, id_usuario, dia_semana, dias):
        return rutina["id"], False
    nombre = nombre_rutina_para_dia(dia_semana, base_del_nombre(rutina["nombre"], rutina["origen"]))
    copia = rutinas_repo.copiar(conn, rutina["id"], id_usuario, nombre, ORIGEN_PLAN)
    plan_service.asignar_rutina(conn, id_usuario, dia_semana, copia, nombre, hoy)
    return copia, True


def _item_del_dia(conn, id_usuario, dia_semana, item_id):
    _exigir_dia(dia_semana)
    entrada = repo.buscar_dia(conn, id_usuario, dia_semana)
    if entrada is None:
        raise NoEncontrado("Ese día no tiene ejercicios")
    item = rutinas_repo.buscar_item(conn, item_id)
    if item is None or item["id_rutina"] != entrada["id_rutina"]:
        raise NoEncontrado("Ejercicio no encontrado en este día")
    return entrada, item


def _item_en(conn, id_rutina, item, copiada):
    """Tras copiar la rutina, el mismo ejercicio en la copia (misma posición)."""
    return rutinas_repo.item_por_orden(conn, id_rutina, item["orden"]) if copiada else item


# ---- Casos de uso -----------------------------------------------------------------------

def agregar(id_usuario, dia_semana, datos):
    _exigir_dia(dia_semana)
    id_ejercicio = _exigir_id(datos.get("ejercicio_id"), "ejercicio_id")
    explicitos = campos_validados(datos, exigir_alguno=False)
    hoy = tiempo.hoy().isoformat()

    with conexion() as conn:
        ejercicio = ejercicios_repo.buscar_por_id(conn, id_ejercicio)
        if ejercicio is None:
            raise NoEncontrado("Ejercicio no encontrado")
        entrada = repo.buscar_dia(conn, id_usuario, dia_semana)
        if entrada is not None and rutinas_repo.contiene_ejercicio(conn, entrada["id_rutina"], id_ejercicio):
            raise Conflicto("Ese ejercicio ya está en este día")

        recomendacion, _ = recomendaciones.para_usuario(conn, ejercicio, id_usuario)
        valores = {**valores_por_defecto(recomendacion), **explicitos}

        if entrada is None:
            musculo = ejercicio["musculo_principal"] or ejercicio["grupo_muscular"]
            nombre = nombre_rutina_para_dia(dia_semana, musculo)
            nivel = recomendacion["nivel"] if recomendacion else "principiante"
            id_rutina = rutinas_repo.crear(conn, id_usuario, nombre, "", "general", nivel, 45, [], ORIGEN_PLAN)
            plan_service.asignar_rutina(conn, id_usuario, dia_semana, id_rutina, nombre, hoy)
            copiada = False
        else:
            id_rutina, copiada = _rutina_para_editar(conn, id_usuario, dia_semana, entrada, hoy)
            total = len(rutinas_repo.items_de_rutinas(conn, [id_rutina])[id_rutina])
            if total >= rutinas_service.MAX_EJERCICIOS:
                raise SolicitudInvalida(f"Un día admite máximo {rutinas_service.MAX_EJERCICIOS} ejercicios")

        orden = rutinas_repo.siguiente_orden(conn, id_rutina)
        item_id = rutinas_repo.agregar_item(conn, id_rutina, orden, {"id_ejercicio": id_ejercicio, **valores})
        item = rutinas_repo.buscar_item(conn, item_id)
        # El músculo del ejercicio contra los DEMÁS días (el propio día no cuenta)
        grupos_por_dia, _ = plan_service.grupos_del_plan(conn, id_usuario)
        avisos = plan_service.avisos_de_descanso(dia_semana, {ejercicio["grupo_muscular"]}, grupos_por_dia)
        peso = plan_service.peso_corporal(conn, id_usuario)

    return {"item": item_a_json(item, peso), "rutina_copiada": copiada, "avisos": avisos}


def editar(id_usuario, dia_semana, item_id, datos):
    cambios = campos_validados(datos, exigir_alguno=True)
    hoy = tiempo.hoy().isoformat()
    with conexion() as conn:
        entrada, item = _item_del_dia(conn, id_usuario, dia_semana, item_id)
        id_rutina, copiada = _rutina_para_editar(conn, id_usuario, dia_semana, entrada, hoy)
        item = _item_en(conn, id_rutina, item, copiada)
        rutinas_repo.actualizar_item(conn, item["item_id"], cambios)
        item = rutinas_repo.buscar_item(conn, item["item_id"])
        peso = plan_service.peso_corporal(conn, id_usuario)
    return {"item": item_a_json(item, peso), "rutina_copiada": copiada}


def quitar(id_usuario, dia_semana, item_id):
    """Quita el ejercicio. Si la rutina del plan queda vacía se elimina y el día queda en descanso."""
    hoy = tiempo.hoy().isoformat()
    with conexion() as conn:
        entrada, item = _item_del_dia(conn, id_usuario, dia_semana, item_id)
        id_rutina, copiada = _rutina_para_editar(conn, id_usuario, dia_semana, entrada, hoy)
        item = _item_en(conn, id_rutina, item, copiada)
        rutinas_repo.quitar_item(conn, item["item_id"])

        dia_en_descanso = not rutinas_repo.items_de_rutinas(conn, [id_rutina])[id_rutina]
        if dia_en_descanso:
            # Tras _rutina_para_editar la rutina es siempre propia, de origen 'plan' y solo de este día
            plan_service.quitar_dia(conn, id_usuario, dia_semana, hoy)
            # Si una sesión cumplida la usa (por ejemplo hoy) se conserva para no perder su nombre en el calendario
            if not repo.rutina_en_algun_plan(conn, id_rutina) and not repo.rutina_con_sesiones(conn, id_rutina):
                rutinas_repo.eliminar(conn, id_rutina)
        dia = plan_service.dia_a_json(conn, id_usuario, dia_semana)

    return {"rutina_copiada": copiada, "dia_en_descanso": dia_en_descanso, "dia": dia}


def previsualizar(id_usuario, ejercicio_id=None, rutina_id=None):
    """Avisos de 48 h de poner el ejercicio (o la rutina) en cada uno de los 7 días. No guarda nada."""
    if (ejercicio_id is None) == (rutina_id is None):
        raise SolicitudInvalida("Indica ejercicio_id o rutina_id (solo uno)")
    with conexion() as conn:
        if ejercicio_id is not None:
            ejercicio = ejercicios_repo.buscar_por_id(conn, _id_de_query(ejercicio_id, "ejercicio_id"))
            if ejercicio is None:
                raise NoEncontrado("Ejercicio no encontrado")
            grupos = {ejercicio["grupo_muscular"]}
        else:
            id_rutina = _id_de_query(rutina_id, "rutina_id")
            if rutinas_repo.buscar_visible(conn, id_rutina, id_usuario) is None:
                raise NoEncontrado("Rutina no encontrada")
            # Músculo principal de cada ejercicio de la rutina, sin duplicados
            grupos = repo.grupos_por_rutina(conn, [id_rutina])[id_rutina]
        grupos_por_dia, _ = plan_service.grupos_del_plan(conn, id_usuario)

    return [
        {
            "dia": dia,
            "nombre_dia": nombre_dia,
            "tiene_rutina": dia in grupos_por_dia,
            "avisos": plan_service.avisos_de_descanso(dia, grupos, grupos_por_dia),
        }
        for dia, nombre_dia in DIAS_SEMANA.items()
    ]
