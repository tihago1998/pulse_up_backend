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
    sembrar_recomendaciones(conn)
    sembrar_met(conn)


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
    "descanso_seg", "tipo_recomendacion", "id_externo", "fuente", "referencia_fuerza",
    "recomendacion_override",
)
_LISTAS = ("musculos_secundarios", "ambientes", "pasos", "instrucciones", "errores_comunes")


def _valores_ampliados(e):
    datos = dict(e)
    datos["instrucciones"] = e["pasos"]  # la app actual lee "instrucciones": reciben los pasos nuevos
    datos["fuente"] = "free-exercise-db" if e.get("id_externo") else "PulseUp"
    for campo in _LISTAS:
        datos[campo] = json.dumps(datos[campo], ensure_ascii=False)
    if datos.get("recomendacion_override") is not None:
        datos["recomendacion_override"] = json.dumps(datos["recomendacion_override"], ensure_ascii=False)
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


# ---- Recomendaciones -----------------------------------------------------------------

_CAMPOS_REGLA = (
    "unidad", "reps_min", "reps_max", "series_min", "series_max", "descanso_seg", "rir", "dias_semana", "rpe", "nota",
)


def ratios_por_nivel_app(fila):
    """Pasa una fila de proporciones de la guía a los 3 niveles de la app.

    La guía tiene 4 niveles (beginner, novice, intermediate, advanced) y la app 3. Decisión:
    principiante = promedio de beginner y novice (alguien que empieza pero ya pasó las primeras
    semanas), intermedio = intermediate y avanzado = advanced. Si la fila ya trae los niveles de la
    app (por ejemplo la prensa, que no distingue sexo) se usan tal cual.
    """
    if "principiante" in fila:
        return {nivel: fila[nivel] for nivel in ("principiante", "intermedio", "avanzado")}
    return {
        "principiante": round((fila["beginner"] + fila["novice"]) / 2, 4),
        "intermedio": fila["intermediate"],
        "avanzado": fila["advanced"],
    }


def sembrar_recomendaciones(conn):
    """Reglas y proporciones de fuerza (recomendaciones_reglas.json). Upsert idempotente: editar el
    JSON y reiniciar actualiza los valores sin duplicar filas."""
    datos = _leer("recomendaciones_reglas.json")
    columnas = ", ".join(_CAMPOS_REGLA)
    marcas = ", ".join("?" * len(_CAMPOS_REGLA))
    actualizar = ", ".join(f"{c} = excluded.{c}" for c in _CAMPOS_REGLA)
    for r in datos["reglas"]:
        conn.execute(
            f"""
            INSERT INTO recomendacion_regla (tipo, nivel, {columnas}) VALUES (?, ?, {marcas})
            ON CONFLICT (tipo, nivel) DO UPDATE SET {actualizar}
            """,
            (r["tipo"], r["nivel"], *[r.get(c) for c in _CAMPOS_REGLA]),
        )
    for fila in datos["proporciones"]:
        for nivel, ratio in ratios_por_nivel_app(fila).items():
            conn.execute(
                """
                INSERT INTO referencia_fuerza_ratio (clave, sexo, nivel, ratio) VALUES (?, ?, ?, ?)
                ON CONFLICT (clave, sexo, nivel) DO UPDATE SET ratio = excluded.ratio
                """,
                (fila["clave"], fila["sexo"], nivel, ratio),
            )


# ---- MET para las calorías aproximadas ---------------------------------------------------

def sembrar_met(conn):
    """MET y código del Compendium de cada ejercicio (met_ejercicios.json). Es idempotente: solo
    hace UPDATE por nombre, así que correrlo varias veces deja los mismos valores y nunca crea filas.
    La categoría y la marca `verificado` quedan en el JSON como referencia (no se guardan)."""
    for e in _leer("met_ejercicios.json")["ejercicios"]:
        conn.execute(
            "UPDATE ejercicio SET met = ?, codigo_compendio = ? WHERE nombre = ?",
            (e["met"], e["codigo_compendio"], e["nombre"]),
        )
