"""Importador del catálogo ampliado: descarga las 2 fotos de cada ejercicio y las registra.

Uso (desde la raíz del proyecto, con el entorno virtual activo):

    python -m tools.importar_catalogo                # usa PULSEUP_DB_NAME o pulseup.db
    python -m tools.importar_catalogo --db otra.db   # otra base de datos
    python -m tools.importar_catalogo --forzar       # vuelve a descargar aunque ya existan
    python -m tools.importar_catalogo --verificar    # además comprueba los id_externo contra el dataset

Qué hace, en orden (todo es idempotente, se puede repetir sin duplicar nada):
1. Crea las tablas que falten y siembra el catálogo (pulseup/seeds/catalogo_seleccion.json).
2. Por cada ejercicio con id_externo descarga exercises/<id>/0.jpg y 1.jpg de free-exercise-db a
   pulseup/static/ejercicios/<id>/ (si ya están, no las vuelve a bajar).
3. Registra cada foto en `ejercicio_imagen` (upsert por ejercicio y orden).

Si una foto no se puede descargar se anota en pulseup/static/ejercicios/errores_importacion.log
y se sigue con las demás. Para cambiar de proveedor de fotos basta con otro importador que
escriba en `ejercicio_imagen` con su propia fuente y licencia: el resto del catálogo no cambia.
"""
import argparse
import json
import os
import sqlite3
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from pulseup import inicializar_base_de_datos  # noqa: E402  (después de ajustar sys.path)

SEMILLA = RAIZ / "pulseup" / "seeds" / "catalogo_seleccion.json"
DESTINO = RAIZ / "pulseup" / "static" / "ejercicios"
URL_BASE = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main"
URL_PUBLICA = "/static/ejercicios"

FUENTE = "free-exercise-db"
LICENCIA = "Unlicense (repositorio); origen de las fotos no documentado"
AUTOR = None
ATRIBUCION = "Fotos del repositorio free-exercise-db de yuhonas (github.com/yuhonas/free-exercise-db)"

ORDENES = (0, 1)  # 0 = posición inicial, 1 = posición final
_JPEG = b"\xff\xd8\xff"


def descargar_http(url, archivo, timeout=30):
    """Descarga `url` a `archivo`. Escribe primero un temporal para no dejar fotos a medias."""
    peticion = urllib.request.Request(url, headers={"User-Agent": "pulseup-importador/1.0"})
    with urllib.request.urlopen(peticion, timeout=timeout) as respuesta:
        datos = respuesta.read()
    if not datos.startswith(_JPEG):
        raise ValueError("la respuesta no es una imagen JPEG")
    archivo.parent.mkdir(parents=True, exist_ok=True)
    temporal = archivo.with_suffix(".part")
    temporal.write_bytes(datos)
    os.replace(temporal, archivo)


def leer_seleccion():
    with open(SEMILLA, encoding="utf-8") as fh:
        return json.load(fh)


def _registrar(conn, id_ejercicio, orden, url):
    conn.execute(
        """
        INSERT INTO ejercicio_imagen (ejercicio_id, orden, url, fuente, licencia, autor, atribucion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (ejercicio_id, orden) DO UPDATE SET
            url = excluded.url, fuente = excluded.fuente, licencia = excluded.licencia,
            autor = excluded.autor, atribucion = excluded.atribucion
        """,
        (id_ejercicio, orden, url, FUENTE, LICENCIA, AUTOR, ATRIBUCION),
    )


def importar(db_name, destino=DESTINO, descargar=descargar_http, url_base=URL_BASE, forzar=False, salida=print):
    """Importa las fotos y devuelve un resumen. `descargar(url, archivo)` se puede sustituir (pruebas)."""
    destino = Path(destino)
    inicializar_base_de_datos(db_name)
    resumen = {"ejercicios": 0, "descargadas": 0, "ya_estaban": 0, "registradas": 0, "fallos": []}

    conn = sqlite3.connect(db_name)
    try:
        for e in leer_seleccion():
            id_externo = e.get("id_externo")
            if not id_externo:
                continue
            fila = conn.execute("SELECT id FROM ejercicio WHERE id_externo = ?", (id_externo,)).fetchone()
            if fila is None:
                resumen["fallos"].append((id_externo, None, "el ejercicio no está en la base de datos"))
                continue
            resumen["ejercicios"] += 1
            for orden in ORDENES:
                archivo = destino / id_externo / f"{orden}.jpg"
                if forzar or not archivo.exists():
                    url_origen = f"{url_base}/exercises/{urllib.parse.quote(id_externo)}/{orden}.jpg"
                    try:
                        descargar(url_origen, archivo)
                    except Exception as exc:  # se anota y se sigue con las demás
                        resumen["fallos"].append((id_externo, orden, str(exc) or type(exc).__name__))
                        continue
                    resumen["descargadas"] += 1
                else:
                    resumen["ya_estaban"] += 1
                _registrar(conn, fila[0], orden, f"{URL_PUBLICA}/{id_externo}/{orden}.jpg")
                resumen["registradas"] += 1
        conn.commit()
    finally:
        conn.close()

    destino.mkdir(parents=True, exist_ok=True)
    with open(destino / "errores_importacion.log", "w", encoding="utf-8") as log:
        for id_externo, orden, error in resumen["fallos"]:
            log.write(f"{id_externo}\t{orden}\t{error}\n")

    salida(
        f"Ejercicios con fotos: {resumen['ejercicios']} | descargadas: {resumen['descargadas']} | "
        f"ya estaban: {resumen['ya_estaban']} | registradas: {resumen['registradas']} | "
        f"fallos: {len(resumen['fallos'])}"
    )
    for id_externo, orden, error in resumen["fallos"]:
        salida(f"  FALLO {id_externo} [{orden}]: {error}")
    return resumen


def verificar_ids(url_base=URL_BASE, salida=print):
    """Comprueba que cada id_externo de la selección exista en dist/exercises.json y tenga 2 fotos."""
    with urllib.request.urlopen(f"{url_base}/dist/exercises.json", timeout=60) as respuesta:
        dataset = {e["id"]: e for e in json.load(respuesta)}
    problemas = []
    for e in leer_seleccion():
        id_externo = e.get("id_externo")
        if id_externo and len(dataset.get(id_externo, {}).get("images", [])) != 2:
            problemas.append(id_externo)
    salida(f"Verificación: {len(problemas)} id_externo sin 2 fotos en el dataset {problemas or ''}")
    return problemas


def main(argv=None):
    from dotenv import load_dotenv

    load_dotenv()
    parser = argparse.ArgumentParser(description="Descarga y registra las fotos del catálogo de ejercicios.")
    parser.add_argument("--db", default=os.environ.get("PULSEUP_DB_NAME", "pulseup.db"))
    parser.add_argument("--destino", default=str(DESTINO))
    parser.add_argument("--forzar", action="store_true", help="vuelve a descargar las fotos existentes")
    parser.add_argument("--verificar", action="store_true", help="comprueba los id_externo contra el dataset")
    args = parser.parse_args(argv)
    if args.verificar:
        verificar_ids()
    resumen = importar(args.db, destino=args.destino, forzar=args.forzar)
    return 1 if resumen["fallos"] else 0


if __name__ == "__main__":
    sys.exit(main())
