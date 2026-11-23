"""Consulta del catálogo de ejercicios."""
from pulseup.core.database import conexion
from pulseup.core.dominio import AMBIENTES, NIVELES
from pulseup.core.errors import NoEncontrado, SolicitudInvalida
from pulseup.modules.ejercicios import repository as repo
from pulseup.modules.ejercicios.schemas import ejercicio_detalle_a_json, ejercicio_resumen_a_json
from pulseup.modules.perfil_fisico import repository as perfil_fisico_repo

LIMIT_POR_DEFECTO = 20
LIMIT_MAXIMO = 100

MOTIVO_SIN_PERFIL = "Completa tu perfil físico para ver el peso recomendado"
# Pendiente: aún no existe el módulo de recomendaciones (series, repeticiones y peso)
MOTIVO_PENDIENTE = "La recomendación personalizada todavía no está disponible"


def _entero(valor, nombre, minimo):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise SolicitudInvalida(f"{nombre} debe ser un número entero") from None
    if numero < minimo:
        raise SolicitudInvalida(f"{nombre} debe ser mayor o igual a {minimo}")
    return numero


def _paginacion(limit, offset, formato):
    """None si no se pidió paginar (forma actual: todos los ejercicios). Si no, (limit, offset)."""
    if limit is None and offset is None and formato != "paginado":
        return None
    limite = LIMIT_POR_DEFECTO if limit is None else min(_entero(limit, "limit", 1), LIMIT_MAXIMO)
    desde = 0 if offset is None else _entero(offset, "offset", 0)
    return limite, desde


def listar(musculo=None, equipo=None, nivel=None, texto=None, ambiente=None, limit=None, offset=None, formato=None):
    """{"ejercicios": [...], "total": n}. Si se pagina (limit, offset o formato=paginado) añade
    "items" (la misma lista), "limit" y "offset". Sin paginar devuelve todos, como antes."""
    if nivel and nivel not in NIVELES:
        raise SolicitudInvalida("Nivel no válido. Usa: " + ", ".join(NIVELES))
    if ambiente and ambiente not in AMBIENTES:
        raise SolicitudInvalida("Ambiente no válido. Usa: " + ", ".join(AMBIENTES))
    pagina = _paginacion(limit, offset, formato)
    filtros = dict(musculo=musculo, equipo=equipo, nivel=nivel, texto=(texto or "").strip() or None, ambiente=ambiente)
    with conexion() as conn:
        total = repo.contar(conn, **filtros)
        if pagina is None:
            filas = repo.listar(conn, **filtros)
        else:
            filas = repo.listar(conn, **filtros, limit=pagina[0], offset=pagina[1])
        ejercicios = [ejercicio_resumen_a_json(f) for f in filas]
    respuesta = {"ejercicios": ejercicios, "total": total}
    if pagina is not None:
        respuesta.update({"items": ejercicios, "limit": pagina[0], "offset": pagina[1]})
    return respuesta


def _recomendacion(conn, id_usuario):
    """(recomendacion, motivo). Por ahora la recomendación siempre es None: queda pendiente
    hasta que exista el módulo de recomendaciones; el motivo le dice a la app qué mostrar."""
    if perfil_fisico_repo.buscar(conn, id_usuario) is None:
        return None, MOTIVO_SIN_PERFIL
    return None, MOTIVO_PENDIENTE


def detalle(id_ejercicio, id_usuario):
    with conexion() as conn:
        fila = repo.buscar_por_id(conn, id_ejercicio)
        if fila is None:
            raise NoEncontrado("Ejercicio no encontrado")
        recomendacion, motivo = _recomendacion(conn, id_usuario)
        return ejercicio_detalle_a_json(fila, repo.imagenes(conn, id_ejercicio), recomendacion, motivo)


def filtros():
    """Valores disponibles para armar los filtros de la pantalla."""
    with conexion() as conn:
        usados = repo.ambientes_usados(conn)
        return {
            "musculos": repo.valores_distintos(conn, "grupo_muscular"),
            "equipos": repo.valores_distintos(conn, "equipo"),
            "niveles": list(NIVELES),
            "ambientes": [a for a in AMBIENTES if a in usados],
        }


def creditos():
    """Fuentes, licencias y atribuciones de las fotos del catálogo."""
    with conexion() as conn:
        filas = repo.creditos(conn)
    return {
        "creditos": [
            {
                "fuente": f["fuente"],
                "licencia": f["licencia"],
                "autor": f["autor"],
                "atribucion": f["atribucion"],
                "imagenes": f["imagenes"],
            }
            for f in filas
        ],
        "textos": "Pasos, respiración, errores comunes y variantes redactados por el equipo de PulseUp.",
    }
