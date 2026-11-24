"""Forma JSON del plan semanal, las sesiones y el calendario."""
from pulseup.core.dominio import DIAS_SEMANA


def rutina_corta(id_rutina, nombre):
    """Referencia mínima a una rutina. None si la rutina ya no existe."""
    if nombre is None:
        return None
    return {"id": id_rutina, "nombre": nombre}


def item_a_json(fila):
    """Un ejercicio de la rutina de un día. Con unidad segundos o minutos, `repeticiones` es la duración."""
    return {
        "item_id": fila["item_id"],
        "ejercicio_id": fila["id_ejercicio"],
        "nombre": fila["nombre"],
        "musculo_principal": fila["musculo_principal"],
        "imagen_miniatura": fila["imagen_miniatura"],
        "series": fila["series"],
        "repeticiones": fila["repeticiones"],
        "unidad": fila["unidad"],
        "peso_kg": fila["peso_kg"],
        "descanso_seg": fila["descanso_seg"],
    }


def dia_plan_a_json(dia_semana, fila=None, grupos=(), ejercicios=()):
    """Un día del plan. `fila` None significa día de descanso (y `ejercicios` vacío)."""
    rutina = None
    if fila is not None:
        rutina = {
            "id": fila["id_rutina"],
            "nombre": fila["nombre"],
            "grupos_musculares": sorted(grupos),
        }
    return {
        "dia_semana": dia_semana,
        "nombre_dia": DIAS_SEMANA[dia_semana],
        "rutina": rutina,
        "ejercicios": [item_a_json(f) for f in ejercicios] if fila is not None else [],
    }


def conflicto_a_json(grupo, dia_semana):
    return {"grupo": grupo, "dia_semana": dia_semana, "nombre_dia": DIAS_SEMANA[dia_semana]}


def aviso_a_json(musculo, dia_conflicto, mensaje):
    return {"tipo": "descanso_48h", "musculo": musculo, "dia_conflicto": dia_conflicto, "mensaje": mensaje}


def dia_calendario_a_json(fecha, estado, rutina):
    return {"fecha": fecha.isoformat(), "dia_semana": fecha.isoweekday(), "estado": estado, "rutina": rutina}


def incumplido_a_json(fecha, vigencia):
    return {
        "fecha": fecha.isoformat(),
        "dia_semana": fecha.isoweekday(),
        "nombre_dia": DIAS_SEMANA[fecha.isoweekday()],
        "rutina": rutina_corta(vigencia["id_rutina"], vigencia["nombre_rutina"]),
    }
