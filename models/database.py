import sqlite3  # librería estándar de Python para trabajar con bases de datos SQLite

DB_NAME = "pulseup.db"  # nombre del archivo de base de datos; se crea solo la primera vez

def get_connection():
    # Abre (o crea si no existe) el archivo pulseup.db y devuelve una conexión
    conn = sqlite3.connect(DB_NAME)
    # Permite acceder a las columnas por nombre (fila["nombre"]) en vez de por índice (fila[0])
    conn.row_factory = sqlite3.Row
    return conn

def crear_tablas():
    # Abrimos conexión y un "cursor" (el objeto que ejecuta comandos SQL)
    conn = get_connection()
    cur = conn.cursor()

    # Tabla de usuarios: guarda nombre, email único y la contraseña YA encriptada (hash)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Tabla de roles: solo dos filas fijas, Administrador (1) y Usuario (2)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rol (
            id_rol INTEGER PRIMARY KEY,
            nombre_rol TEXT NOT NULL
        )
    """)

    # Tabla puente: relaciona usuarios con roles (un usuario podría tener varios roles a la vez)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuario_rol (
            id_usuario INTEGER NOT NULL,
            id_rol INTEGER NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
            FOREIGN KEY (id_rol) REFERENCES rol(id_rol),
            PRIMARY KEY (id_usuario, id_rol)
        )
    """)

    # Registros de ejercicio de cada usuario (módulo EP-001 de tus historias)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registro_ejercicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            tipo_actividad TEXT NOT NULL,
            duracion_min INTEGER NOT NULL,
            calorias INTEGER,
            fecha TEXT NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        )
    """)

    # Registros de alimentación de cada usuario (módulo EP-002)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registro_alimento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            nombre_alimento TEXT NOT NULL,
            calorias INTEGER,
            categoria TEXT,
            fecha TEXT NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        )
    """)

    # Registros de sueño de cada usuario (módulo EP-003)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registro_sueno (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            horas_dormidas REAL NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS habito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            descripcion TEXT NOT NULL,
            categoria TEXT NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        )
    """)

    # Sembramos los dos roles base. INSERT OR IGNORE evita error si ya existen
    # (por ejemplo, si detienes y vuelves a correr el servidor varias veces)
    cur.execute("INSERT OR IGNORE INTO rol (id_rol, nombre_rol) VALUES (1, 'Administrador')")
    cur.execute("INSERT OR IGNORE INTO rol (id_rol, nombre_rol) VALUES (2, 'Usuario')")
    cur.execute("INSERT OR IGNORE INTO rol (id_rol, nombre_rol) VALUES (3, 'SuperAdministrador')")

    conn.commit()  # guarda los cambios de forma permanente en el archivo .db
    conn.close()   # cierra la conexión