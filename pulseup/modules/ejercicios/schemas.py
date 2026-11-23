"""Forma JSON de un ejercicio."""
import json


def ejercicio_a_json(fila, con_instrucciones=True):
    datos = {
        "id": fila["id"],
        "nombre": fila["nombre"],
        "grupo_muscular": fila["grupo_muscular"],
        "musculos_secundarios": json.loads(fila["musculos_secundarios"]),
        "equipo": fila["equipo"],
        "nivel": fila["nivel"],
    }
    if con_instrucciones:
        datos["instrucciones"] = json.loads(fila["instrucciones"])
    return datos
