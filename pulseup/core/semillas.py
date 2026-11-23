"""Carga el catálogo inicial (ejercicios y rutinas plantilla). Es idempotente."""
import json
from pathlib import Path

CARPETA = Path(__file__).resolve().parent.parent / "seeds"


def _leer(nombre):
    with open(CARPETA / nombre, encoding="utf-8") as archivo:
        return json.load(archivo)


def sembrar_catalogo(conn):
    sembrar_ejercicios_base(conn)
    sembrar_catalogo_ampliado(conn)
    sembrar_rutinas(conn)


def sembrar_ejercicios_base(conn):
    """Los 48 ejercicios originales. INSERT OR IGNORE: nunca cambia ni duplica los existentes."""
    for e in _leer("ejercicios.json"):
        conn.execute(
            """
            INSERT OR IGNORE INTO ejercicio
                (nombre, grupo_muscular, musculos_secundarios, equipo, nivel, instrucciones)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                e["nombre"], e["grupo_muscular"],
                json.dumps(e["musculos_secundarios"], ensure_ascii=False),
                e["equipo"], e["nivel"],
                json.dumps(e["instrucciones"], ensure_ascii=False),
            ),
        )


def sembrar_rutinas(conn):
    for r in _leer("rutinas.json"):
        existe = conn.execute(
            "SELECT 1 FROM rutina WHERE id_usuario IS NULL AND nombre = ?", (r["nombre"],)
        ).fetchone()
        if existe:
            continue
        id_rutina = conn.execute(
            """
            INSERT INTO rutina (id_usuario, nombre, descripcion, objetivo, nivel, duracion_min)
            VALUES (NULL, ?, ?, ?, ?, ?)
            """,
            (r["nombre"], r["descripcion"], r["objetivo"], r["nivel"], r["duracion_min"]),
        ).lastrowid
        for orden, item in enumerate(r["ejercicios"], start=1):
            id_ejercicio = conn.execute(
                "SELECT id FROM ejercicio WHERE nombre = ?", (item["ejercicio"],)
            ).fetchone()["id"]
            conn.execute(
                """
                INSERT INTO rutina_ejercicio
                    (id_rutina, id_ejercicio, orden, series, repeticiones, descanso_seg)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (id_rutina, id_ejercicio, orden, item["series"], item["repeticiones"], item["descanso_seg"]),
            )


# Columnas que el catálogo ampliado escribe en cada ejercicio (además de nombre y grupo_muscular)
_CAMPOS_AMPLIADOS = (
    "musculo_principal", "musculos_secundarios", "equipo", "nivel", "mecanica", "ambientes", "pasos",
    "instrucciones", "respiracion", "errores_comunes", "variante_facil", "variante_dificil",
    "descanso_seg", "tipo_recomendacion", "id_externo", "fuente",
)
_LISTAS = ("musculos_secundarios", "ambientes", "pasos", "instrucciones", "errores_comunes")


def _valores_ampliados(e):
    datos = dict(e)
    datos["instrucciones"] = e["pasos"]  # la app actual lee "instrucciones": reciben los pasos nuevos
    datos["fuente"] = "free-exercise-db" if e.get("id_externo") else "PulseUp"
    for campo in _LISTAS:
        datos[campo] = json.dumps(datos[campo], ensure_ascii=False)
    return [datos.get(campo) for campo in _CAMPOS_AMPLIADOS]


def sembrar_catalogo_ampliado(conn):
    """Selección curada (catalogo_seleccion.json). Es un upsert idempotente.

    Busca primero por id_externo y luego por nombre. Si el ejercicio ya existe lo ACTUALIZA sin
    cambiar su id, su nombre ni su grupo_muscular (las rutinas, el plan y la regla de 48 h
    dependen de ellos). Si no existe lo crea. Correrlo varias veces deja el mismo catálogo.
    """
    asignaciones = ", ".join(f"{campo} = ?" for campo in _CAMPOS_AMPLIADOS)
    columnas = ", ".join(_CAMPOS_AMPLIADOS)
    marcas = ", ".join("?" * len(_CAMPOS_AMPLIADOS))
    for e in _leer("catalogo_seleccion.json"):
        fila = None
        if e.get("id_externo"):
            fila = conn.execute("SELECT id FROM ejercicio WHERE id_externo = ?", (e["id_externo"],)).fetchone()
        if fila is None:
            fila = conn.execute("SELECT id FROM ejercicio WHERE nombre = ?", (e["nombre"],)).fetchone()
        valores = _valores_ampliados(e)
        if fila is not None:
            conn.execute(f"UPDATE ejercicio SET {asignaciones} WHERE id = ?", (*valores, fila[0]))
        else:
            conn.execute(
                f"INSERT INTO ejercicio (nombre, grupo_muscular, {columnas}) VALUES (?, ?, {marcas})",
                (e["nombre"], e["musculo_principal"], *valores),
            )
