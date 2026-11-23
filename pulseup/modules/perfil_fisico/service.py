"""Reglas del perfil físico: validación de datos y cálculo de la edad."""
import math
import re
from datetime import date

from pulseup.core import tiempo
from pulseup.core.database import conexion
from pulseup.core.dominio import (
    EDAD_MAXIMA,
    EDAD_MINIMA,
    ESTATURA_MAX_CM,
    ESTATURA_MIN_CM,
    NIVELES,
    PESO_MAX_KG,
    PESO_MIN_KG,
    SEXOS,
)
from pulseup.core.errors import SolicitudInvalida
from pulseup.modules.perfil_fisico import repository as repo
from pulseup.modules.perfil_fisico.schemas import perfil_a_json

OBLIGATORIOS = ("fecha_nacimiento", "peso_kg", "estatura_cm", "nivel")
_FORMATO_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")


def calcular_edad(nacimiento, hoy):
    """Años cumplidos a la fecha `hoy`. Quien nació un 29 de febrero cumple el 1 de marzo."""
    return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))


def _leer_fecha_nacimiento(valor, hoy):
    if not isinstance(valor, str) or not _FORMATO_FECHA.fullmatch(valor):
        raise SolicitudInvalida("Fecha de nacimiento inválida, usa el formato YYYY-MM-DD")
    try:
        nacimiento = date.fromisoformat(valor)
    except ValueError:
        raise SolicitudInvalida("Fecha de nacimiento inválida, usa el formato YYYY-MM-DD") from None
    if nacimiento > hoy:
        raise SolicitudInvalida("La fecha de nacimiento no puede ser futura")
    edad = calcular_edad(nacimiento, hoy)
    if edad < EDAD_MINIMA:
        raise SolicitudInvalida(f"Debes tener al menos {EDAD_MINIMA} años para usar PulseUp")
    if edad > EDAD_MAXIMA:
        raise SolicitudInvalida(f"Revisa la fecha de nacimiento: la edad máxima es {EDAD_MAXIMA} años")
    return valor


def _leer_medida(valor, campo, minimo, maximo, unidad):
    """Número (int o float, nunca bool ni texto) dentro del rango; se guarda con 1 decimal."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
        raise SolicitudInvalida(f"{campo} debe ser un número")
    if not minimo <= valor <= maximo:
        raise SolicitudInvalida(f"{campo} debe estar entre {minimo} y {maximo} {unidad}")
    return round(float(valor), 1)


def _validar(datos, hoy):
    if not isinstance(datos, dict):
        raise SolicitudInvalida("El cuerpo debe ser un objeto JSON")
    faltan = [campo for campo in OBLIGATORIOS if datos.get(campo) is None]
    if faltan:
        raise SolicitudInvalida("Faltan campos obligatorios: " + ", ".join(faltan))

    sexo = datos.get("sexo")
    if sexo is None:
        sexo = "no_indica"
    elif sexo not in SEXOS:
        raise SolicitudInvalida("Sexo no válido. Usa: " + ", ".join(SEXOS))

    nivel = datos["nivel"]
    if nivel not in NIVELES:
        raise SolicitudInvalida("Nivel no válido. Usa: " + ", ".join(NIVELES))

    return {
        "fecha_nacimiento": _leer_fecha_nacimiento(datos["fecha_nacimiento"], hoy),
        "sexo": sexo,
        "peso_kg": _leer_medida(datos["peso_kg"], "peso_kg", PESO_MIN_KG, PESO_MAX_KG, "kg"),
        "estatura_cm": _leer_medida(datos["estatura_cm"], "estatura_cm", ESTATURA_MIN_CM, ESTATURA_MAX_CM, "cm"),
        "nivel": nivel,
    }


def _a_json(fila):
    edad = calcular_edad(date.fromisoformat(fila["fecha_nacimiento"]), tiempo.hoy())
    return perfil_a_json(fila, edad)


def ver(id_usuario):
    """El perfil del usuario, o None si aún no lo ha llenado."""
    with conexion() as conn:
        fila = repo.buscar(conn, id_usuario)
    return None if fila is None else _a_json(fila)


def guardar(id_usuario, datos):
    limpios = _validar(datos, tiempo.hoy())
    with conexion() as conn:
        repo.guardar(conn, id_usuario, limpios, tiempo.ahora().isoformat(timespec="seconds"))
        fila = repo.buscar(conn, id_usuario)
    return _a_json(fila)


def eliminar(id_usuario):
    """Borra el perfil. No falla si no existía."""
    with conexion() as conn:
        repo.eliminar_de_usuario(conn, id_usuario)
