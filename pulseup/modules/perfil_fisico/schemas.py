"""Forma JSON del perfil físico."""


def perfil_a_json(fila, edad):
    """`edad` se calcula en el servicio con la fecha de hoy; no se guarda."""
    return {
        "fecha_nacimiento": fila["fecha_nacimiento"],
        "edad": edad,
        "sexo": fila["sexo"],
        "peso_kg": fila["peso_kg"],
        "estatura_cm": fila["estatura_cm"],
        "nivel": fila["nivel"],
        "actualizado_en": fila["actualizado_en"],
    }
