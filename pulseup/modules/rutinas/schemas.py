"""Forma JSON de una rutina."""
from pulseup.modules.ejercicios.schemas import ejercicio_a_json


def rutina_a_json(fila):
    return {
        "id": fila["id"],
        "nombre": fila["nombre"],
        "descripcion": fila["descripcion"],
        "objetivo": fila["objetivo"],
        "nivel": fila["nivel"],
        "duracion_min": fila["duracion_min"],
        "total_ejercicios": fila["total_ejercicios"],
        "es_plantilla": fila["id_usuario"] is None,
    }


def rutina_detalle_a_json(fila, filas_ejercicios):
    datos = rutina_a_json(fila)
    datos["ejercicios"] = [
        {
            "orden": f["orden"],
            "series": f["series"],
            "repeticiones": f["repeticiones"],
            "descanso_seg": f["descanso_seg"],
            "ejercicio": ejercicio_a_json(f, con_instrucciones=True),
        }
        for f in filas_ejercicios
    ]
    return datos
