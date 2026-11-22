"""Forma JSON del plan semanal, las sesiones y el calendario."""
from pulseup.core.dominio import DIAS_SEMANA


def rutina_corta(id_rutina, nombre):
    """Referencia mínima a una rutina. None si la rutina ya no existe."""
    if nombre is None:
        return None
    return {"id": id_rutina, "nombre": nombre}


def dia_plan_a_json(dia_semana, fila=None, grupos=()):
    """Un día del plan. `fila` None significa día de descanso."""
    rutina = None
    if fila is not None:
        rutina = {
            "id": fila["id_rutina"],
            "nombre": fila["nombre"],
            "grupos_musculares": sorted(grupos),
        }
    return {"dia_semana": dia_semana, "nombre_dia": DIAS_SEMANA[dia_semana], "rutina": rutina}


def conflicto_a_json(grupo, dia_semana):
    return {"grupo": grupo, "dia_semana": dia_semana, "nombre_dia": DIAS_SEMANA[dia_semana]}


def dia_calendario_a_json(fecha, estado, rutina):
    return {"fecha": fecha.isoformat(), "dia_semana": fecha.isoweekday(), "estado": estado, "rutina": rutina}


def incumplido_a_json(fecha, fila_plan):
    return {
        "fecha": fecha.isoformat(),
        "dia_semana": fecha.isoweekday(),
        "nombre_dia": DIAS_SEMANA[fecha.isoweekday()],
        "rutina": rutina_corta(fila_plan["id_rutina"], fila_plan["nombre"]),
    }
