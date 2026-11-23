"""Recomendación personalizada de series, repeticiones, descanso y peso para un ejercicio.

Las reglas (series y repeticiones por tipo y nivel) y las proporciones de fuerza viven en la base
de datos, sembradas desde pulseup/seeds/recomendaciones_reglas.json. Aquí solo está el cálculo.

Peso de trabajo (solo ejercicios con referencia_fuerza, es decir, la variante exacta de un
levantamiento de referencia):
    1RM de referencia = ratio(levantamiento, sexo, nivel) × min(peso corporal, 113 kg)
    peso = 1RM / (1 + reps / 30)            (Epley, reps = punto medio del rango del nivel + 2)
    × 0.80 si tiene menos de 18 años, × 0.85 si tiene más de 50
    redondeado hacia ABAJO a múltiplos de 2.5 kg, mínimo 2.5 kg
Se suman 2 repeticiones al punto medio para que el peso deje unas 2 repeticiones en reserva
(RIR ~2, como pide la guía): Epley estima el peso máximo para esas repeticiones, no uno cómodo.
El nivel principiante usa el promedio de Beginner y Novice de la guía (ver core/semillas.py).
Si el sexo no es "hombre" (no_indica u otro valor) se usa la columna de mujer: es la más
conservadora. Sin peso corporal o sin edad no se estima el peso (peso_kg = None).
"""
import json
import math
from datetime import date

from pulseup.core import tiempo
from pulseup.core.database import conexion
from pulseup.core.dominio import NIVELES
from pulseup.core.errors import NoEncontrado
from pulseup.modules.ejercicios import repository as ejercicios_repo
from pulseup.modules.perfil_fisico import repository as perfil_fisico_repo
from pulseup.modules.perfil_fisico.service import calcular_edad
from pulseup.modules.recomendaciones import repository as repo

TOPE_PESO_CORPORAL_KG = 113
INCREMENTO_KG = 2.5
PESO_MINIMO_KG = 2.5
FACTOR_MENOR_DE_18 = 0.80
FACTOR_MAYOR_DE_50 = 0.85
REPS_EN_RESERVA = 2

TIPOS_CON_CARGA = ("carga_compuesto", "carga_aislamiento", "carga_brazos")

AVISO = "Es una guía general y no reemplaza a un entrenador ni a un médico."
NOTA_SIN_PESO = (
    "Elige un peso con el que completes el rango bajo de repeticiones con 2–3 en reserva, "
    "y súbelo entre 2 y 10 % cuando superes el rango alto."
)
MOTIVO_SIN_PERFIL = "Completa tu perfil físico para ver la recomendación"
MOTIVO_SIN_REGLA = "Este ejercicio todavía no tiene recomendación"

_CAMPOS_OVERRIDE = ("reps_min", "reps_max", "series_min", "series_max")


# ---- Funciones puras ------------------------------------------------------------------

def peso_epley(una_rm, reps):
    """Peso que se puede levantar `reps` veces según la fórmula de Epley (1RM = peso × (1 + reps/30))."""
    return una_rm / (1 + reps / 30)


def reps_objetivo(reps_min, reps_max):
    """Punto medio del rango, redondeado hacia arriba en los .5 (8–12 → 10, 5–10 → 8)."""
    return math.floor((reps_min + reps_max) / 2 + 0.5)


def reps_para_epley(reps_min, reps_max):
    """Repeticiones con las que se estima el peso: punto medio del rango + 2 en reserva (8–12 → 12)."""
    return reps_objetivo(reps_min, reps_max) + REPS_EN_RESERVA


def redondear_abajo(kg, paso=INCREMENTO_KG):
    """Múltiplo de `paso` inmediatamente inferior (el margen evita errores de coma flotante)."""
    return math.floor(kg / paso + 1e-9) * paso


def factor_edad(edad):
    if edad < 18:
        return FACTOR_MENOR_DE_18
    if edad > 50:
        return FACTOR_MAYOR_DE_50
    return 1.0


def sexo_para_ratio(sexo):
    """Solo "hombre" usa su columna; cualquier otro valor (mujer, no_indica, None) usa la de mujer."""
    return "hombre" if sexo == "hombre" else "mujer"


def calcular_peso_kg(ratio, peso_corporal_kg, reps, edad):
    una_rm = ratio * min(peso_corporal_kg, TOPE_PESO_CORPORAL_KG)
    peso = peso_epley(una_rm, reps) * factor_edad(edad)
    return max(redondear_abajo(peso), PESO_MINIMO_KG)


def aplicar_override(regla, override, nivel):
    """Reglas propias del ejercicio (hoy solo Dominadas) sobre la regla general del tipo."""
    propia = (override or {}).get(nivel) or {}
    return {**regla, **{campo: propia[campo] for campo in _CAMPOS_OVERRIDE if campo in propia}}


def nota_para(tipo, regla, peso_kg):
    if tipo in ("carga_compuesto", "carga_aislamiento") and peso_kg is None:
        return NOTA_SIN_PESO
    return regla.get("nota")


def armar_recomendacion(nivel, regla, peso_kg, nota):
    return {
        "nivel": nivel,
        "unidad": regla["unidad"],
        "reps_min": regla["reps_min"],
        "reps_max": regla["reps_max"],
        "series_min": regla["series_min"],
        "series_max": regla["series_max"],
        "descanso_seg": regla["descanso_seg"],
        "rir": regla["rir"],
        "dias_semana": regla["dias_semana"],
        "rpe": regla["rpe"],
        "peso_kg": peso_kg,
        "nota": nota,
        "aviso": AVISO,
    }


def edad_de(fecha_nacimiento, hoy):
    """Edad en años o None si la fecha falta o no es válida (código defensivo)."""
    if not fecha_nacimiento:
        return None
    try:
        return calcular_edad(date.fromisoformat(fecha_nacimiento), hoy)
    except (TypeError, ValueError):
        return None


# ---- Orquestación -----------------------------------------------------------------------

def _dato(perfil, campo):
    return dict(perfil).get(campo) if perfil is not None else None


def recomendacion_para(conn, ejercicio, perfil, hoy):
    """(recomendacion, motivo) para un ejercicio (fila) y un perfil físico (fila, dict o None).

    El perfil se lee de forma defensiva: sin nivel no hay recomendación; con nivel pero sin peso
    corporal o sin edad se devuelven series y repeticiones con peso_kg = None.
    """
    nivel = _dato(perfil, "nivel")
    if nivel not in NIVELES:
        return None, MOTIVO_SIN_PERFIL
    tipo = ejercicio["tipo_recomendacion"]
    regla = repo.regla(conn, tipo, nivel) if tipo else None
    if regla is None:
        return None, MOTIVO_SIN_REGLA
    override = ejercicio["recomendacion_override"]
    regla = aplicar_override(regla, json.loads(override) if override else None, nivel)

    peso_kg = None
    peso_corporal = _dato(perfil, "peso_kg")
    edad = edad_de(_dato(perfil, "fecha_nacimiento"), hoy)
    clave = ejercicio["referencia_fuerza"]
    if tipo in TIPOS_CON_CARGA and clave and peso_corporal and edad is not None:
        ratio = repo.ratio(conn, clave, sexo_para_ratio(_dato(perfil, "sexo")), nivel)
        if ratio is not None:
            reps = reps_para_epley(regla["reps_min"], regla["reps_max"])
            peso_kg = calcular_peso_kg(ratio, peso_corporal, reps, edad)
    return armar_recomendacion(nivel, regla, peso_kg, nota_para(tipo, regla, peso_kg)), None


def para_usuario(conn, ejercicio, id_usuario):
    """Recomendación del ejercicio para el perfil físico del usuario (dentro de una conexión abierta)."""
    return recomendacion_para(conn, ejercicio, perfil_fisico_repo.buscar(conn, id_usuario), tiempo.hoy())


def obtener(id_ejercicio, id_usuario):
    with conexion() as conn:
        ejercicio = ejercicios_repo.buscar_por_id(conn, id_ejercicio)
        if ejercicio is None:
            raise NoEncontrado("Ejercicio no encontrado")
        recomendacion, motivo = para_usuario(conn, ejercicio, id_usuario)
    return {"recomendacion": recomendacion, "recomendacion_motivo": motivo}
