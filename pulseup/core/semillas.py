"""Carga el catálogo inicial (ejercicios y rutinas plantilla). Es idempotente."""
import json
from pathlib import Path

CARPETA = Path(__file__).resolve().parent.parent / "seeds"


def _leer(nombre):
    with open(CARPETA / nombre, encoding="utf-8") as archivo:
        return json.load(archivo)


def sembrar_catalogo(conn):
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
