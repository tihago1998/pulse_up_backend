"""Tablas de la base de datos. Todo es aditivo: `IF NOT EXISTS`, nada se borra ni se renombra."""
from pulseup.core import roles as R

TABLAS = [
    # Usuarios: la contraseña se guarda YA encriptada (hash)
    """
    CREATE TABLE IF NOT EXISTS usuario (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS rol (
        id_rol INTEGER PRIMARY KEY,
        nombre_rol TEXT NOT NULL
    )
    """,
    # Tabla puente: un usuario puede tener varios roles
    """
    CREATE TABLE IF NOT EXISTS usuario_rol (
        id_usuario INTEGER NOT NULL,
        id_rol INTEGER NOT NULL,
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
        FOREIGN KEY (id_rol) REFERENCES rol(id_rol),
        PRIMARY KEY (id_usuario, id_rol)
    )
    """,
    # Hábitos con fecha. Ya NO alimentan las llamas del Home: estas salen del calendario de rutinas
    # (/api/calendario/). Los endpoints de hábitos se conservan hasta migrar la app.
    """
    CREATE TABLE IF NOT EXISTS habito (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        descripcion TEXT NOT NULL,
        categoria TEXT NOT NULL,
        fecha TEXT NOT NULL,
        completado INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
    )
    """,
    # Catálogo de ejercicios (compartido por todos los usuarios)
    """
    CREATE TABLE IF NOT EXISTS ejercicio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        grupo_muscular TEXT NOT NULL,
        musculos_secundarios TEXT NOT NULL DEFAULT '[]',
        equipo TEXT NOT NULL,
        nivel TEXT NOT NULL,
        instrucciones TEXT NOT NULL DEFAULT '[]'
    )
    """,
    "CREATE INDEX IF NOT EXISTS ix_ejercicio_grupo ON ejercicio(grupo_muscular)",
    "CREATE INDEX IF NOT EXISTS ix_ejercicio_equipo ON ejercicio(equipo)",
    # Rutinas: con id_usuario NULL son plantillas del sistema; con id_usuario son del usuario
    """
    CREATE TABLE IF NOT EXISTS rutina (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER,
        nombre TEXT NOT NULL,
        descripcion TEXT NOT NULL DEFAULT '',
        objetivo TEXT NOT NULL,
        nivel TEXT NOT NULL,
        duracion_min INTEGER NOT NULL DEFAULT 45,
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
    )
    """,
    "CREATE UNIQUE INDEX IF NOT EXISTS ux_rutina_plantilla ON rutina(nombre) WHERE id_usuario IS NULL",
    "CREATE INDEX IF NOT EXISTS ix_rutina_usuario ON rutina(id_usuario)",
    # Qué ejercicios lleva cada rutina, en qué orden y con cuántas series
    """
    CREATE TABLE IF NOT EXISTS rutina_ejercicio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_rutina INTEGER NOT NULL,
        id_ejercicio INTEGER NOT NULL,
        orden INTEGER NOT NULL,
        series INTEGER NOT NULL,
        repeticiones TEXT NOT NULL,
        descanso_seg INTEGER NOT NULL DEFAULT 60,
        FOREIGN KEY (id_rutina) REFERENCES rutina(id),
        FOREIGN KEY (id_ejercicio) REFERENCES ejercicio(id),
        UNIQUE (id_rutina, orden)
    )
    """,
    # Plan semanal: qué rutina toca cada día (1 = lunes ... 7 = domingo). Sin fila = descanso.
    # creado_en (YYYY-MM-DD) es solo informativo: el calendario ya usa plan_historial. No se borra
    # porque el esquema es aditivo (nunca se eliminan columnas).
    """
    CREATE TABLE IF NOT EXISTS plan_dia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
        id_rutina INTEGER NOT NULL,
        creado_en TEXT NOT NULL,  -- informativo, ver comentario arriba
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
        FOREIGN KEY (id_rutina) REFERENCES rutina(id),
        UNIQUE (id_usuario, dia_semana)
    )
    """,
    "CREATE INDEX IF NOT EXISTS ix_plan_dia_rutina ON plan_dia(id_rutina)",
    # Historial del plan: qué rutina estuvo planificada cada día de la semana y durante qué fechas.
    # vigente_hasta es excluyente y NULL mientras siga vigente. El calendario evalúa el pasado con
    # este historial, así cambiar o quitar un día del plan no reescribe lo que ya pasó.
    # nombre_rutina se copia para no perder el nombre si después se elimina la rutina.
    """
    CREATE TABLE IF NOT EXISTS plan_historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 7),
        id_rutina INTEGER NOT NULL,
        nombre_rutina TEXT NOT NULL,
        vigente_desde TEXT NOT NULL,
        vigente_hasta TEXT,
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
    )
    """,
    "CREATE INDEX IF NOT EXISTS ix_plan_historial_usuario ON plan_historial(id_usuario, dia_semana)",
    # Sesiones: la rutina del día marcada como cumplida (una por usuario y fecha).
    # id_rutina no lleva FK a propósito: el historial se conserva aunque luego se borre la rutina.
    """
    CREATE TABLE IF NOT EXISTS sesion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        id_rutina INTEGER NOT NULL,
        completada_en TEXT NOT NULL,
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
        UNIQUE (id_usuario, fecha)
    )
    """,
]


def crear_esquema(conn):
    for sentencia in TABLAS:
        conn.execute(sentencia)
    # Migración: bases creadas antes de existir "completado" en habito
    columnas = [fila["name"] for fila in conn.execute("PRAGMA table_info(habito)").fetchall()]
    if "completado" not in columnas:
        conn.execute("ALTER TABLE habito ADD COLUMN completado INTEGER NOT NULL DEFAULT 0")
    # Migración: planes creados antes de existir el historial. Cada día planificado sin vigencia
    # abierta recibe una desde su creado_en. Es idempotente.
    conn.execute(
        """
        INSERT INTO plan_historial (id_usuario, dia_semana, id_rutina, nombre_rutina, vigente_desde)
        SELECT p.id_usuario, p.dia_semana, p.id_rutina, r.nombre, p.creado_en
        FROM plan_dia p
        JOIN rutina r ON r.id = p.id_rutina
        WHERE NOT EXISTS (
            SELECT 1 FROM plan_historial h
            WHERE h.id_usuario = p.id_usuario AND h.dia_semana = p.dia_semana AND h.vigente_hasta IS NULL
        )
        """
    )


def sembrar_roles(conn):
    # INSERT OR IGNORE: no falla si el servidor se reinicia y los roles ya existen
    for id_rol, nombre in R.ROLES_BASE:
        conn.execute("INSERT OR IGNORE INTO rol (id_rol, nombre_rol) VALUES (?, ?)", (id_rol, nombre))
