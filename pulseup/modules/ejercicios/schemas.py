"""Forma JSON de un ejercicio."""
import json


def _lista(valor):
    return json.loads(valor) if valor else []


def ejercicio_a_json(fila, con_instrucciones=True):
    """Forma básica. La usan también las rutinas: no cambiarla para no romper sus respuestas."""
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


def ejercicio_resumen_a_json(fila):
    """Elemento del listado: la forma básica + los campos del catálogo ampliado."""
    datos = ejercicio_a_json(fila, con_instrucciones=False)
    datos.update(
        {
            "musculo_principal": fila["musculo_principal"] or fila["grupo_muscular"],
            "ambientes": _lista(fila["ambientes"]),
            "mecanica": fila["mecanica"],
            "imagen_miniatura": fila["imagen_miniatura"],
        }
    )
    return datos


def ejercicio_detalle_a_json(fila, imagenes, recomendacion, recomendacion_motivo):
    datos = ejercicio_a_json(fila, con_instrucciones=True)
    lista_imagenes = [{"orden": i["orden"], "url": i["url"]} for i in imagenes]
    datos.update(
        {
            "musculo_principal": fila["musculo_principal"] or fila["grupo_muscular"],
            "ambientes": _lista(fila["ambientes"]),
            "mecanica": fila["mecanica"],
            "imagen_miniatura": lista_imagenes[0]["url"] if lista_imagenes and lista_imagenes[0]["orden"] == 0 else None,
            "pasos": _lista(fila["pasos"]),
            "respiracion": fila["respiracion"],
            "errores_comunes": _lista(fila["errores_comunes"]),
            "variante_facil": fila["variante_facil"],
            "variante_dificil": fila["variante_dificil"],
            "descanso_seg": fila["descanso_seg"],
            "imagenes": lista_imagenes,
            "recomendacion": recomendacion,
            "recomendacion_motivo": recomendacion_motivo,
        }
    )
    return datos
