"""Calorías aproximadas de un ejercicio, de un día del plan y de una sesión.

Fórmula bruta estándar del Compendium of Physical Activities:
    kcal = MET × peso corporal (kg) × horas
- El peso corporal es el real del perfil físico, SIN el tope de 113 kg que usa la recomendación de peso.
- Horas = series × (tiempo de trabajo + descanso) / 3600. Tiempo de trabajo: repeticiones × 3 s,
  la duración en segundos, o minutos × 60. En minutos (cardio) no se suma descanso.
- Se redondea al múltiplo de 5 más cercano, con un mínimo de 5 kcal.
- Sin peso corporal o sin MET no se estima nada (None): nunca se usa un peso promedio.
Todo aquí son funciones puras (no tocan la base de datos).
"""
import math
import re

SEGUNDOS_POR_REPETICION = 3
PASO_KCAL = 5
MINIMO_KCAL = 5

# Fórmula bruta (MET totales). Para calorías NETAS (solo lo gastado por encima del reposo) se
# restaría 1 MET: cambiar MET_REPOSO_A_RESTAR a 1.0. No se usa: el Compendium publica valores brutos.
MET_REPOSO_A_RESTAR = 0.0

NOTA = "Estimación aproximada: el gasto real varía según la persona y la intensidad."

_NUMERO = r"\d+(?:[.,]\d+)?"
_RANGO = re.compile(rf"^\s*({_NUMERO})\s*(?:-|–|a)\s*({_NUMERO})\s*$")
_SOLO_NUMERO = re.compile(rf"^\s*({_NUMERO})\s*$")


def _float(texto):
    return float(texto.replace(",", "."))


def valor_repeticiones(repeticiones):
    """Número de repeticiones (o duración) a partir del texto guardado: "10" -> 10, "8-12" -> 10
    (punto medio). None si no se puede leer (por ejemplo "al fallo")."""
    if repeticiones is None:
        return None
    if isinstance(repeticiones, (int, float)) and not isinstance(repeticiones, bool):
        return float(repeticiones)
    texto = str(repeticiones)
    rango = _RANGO.match(texto)
    if rango:
        return (_float(rango.group(1)) + _float(rango.group(2))) / 2
    numero = _SOLO_NUMERO.match(texto)
    return _float(numero.group(1)) if numero else None


def duracion_horas(series, repeticiones, unidad, descanso_seg):
    """Tiempo total del ejercicio en horas, o None si faltan datos."""
    valor = valor_repeticiones(repeticiones)
    if valor is None or not series:
        return None
    if unidad == "minutos":
        return series * valor * 60 / 3600  # cardio continuo: sin descanso
    trabajo = valor if unidad == "segundos" else valor * SEGUNDOS_POR_REPETICION
    return series * (trabajo + (descanso_seg or 0)) / 3600


def kcal_brutas(met, peso_corporal_kg, horas):
    """La fórmula, en un solo lugar."""
    return (met - MET_REPOSO_A_RESTAR) * peso_corporal_kg * horas


def redondear_kcal(kcal):
    """Múltiplo de 5 más cercano (en el punto medio hacia arriba), mínimo 5."""
    return max(MINIMO_KCAL, int(math.floor(kcal / PASO_KCAL + 0.5)) * PASO_KCAL)


def calorias_ejercicio(met, peso_corporal_kg, series, repeticiones, unidad, descanso_seg):
    """kcal aproximadas del ejercicio, redondeadas, o None si falta el MET, el peso o el tiempo."""
    if not met or not peso_corporal_kg:
        return None
    horas = duracion_horas(series, repeticiones, unidad, descanso_seg)
    if horas is None:
        return None
    return redondear_kcal(kcal_brutas(met, peso_corporal_kg, horas))


def total(calorias):
    """Suma de las calorías de varios ejercicios; los que no se pudieron estimar no cuentan.
    None si ninguno tiene estimación."""
    conocidas = [c for c in calorias if c is not None]
    return sum(conocidas) if conocidas else None


def peso_corporal(perfil):
    """Peso real del perfil físico (fila, dict o None)."""
    if perfil is None:
        return None
    return dict(perfil).get("peso_kg")
