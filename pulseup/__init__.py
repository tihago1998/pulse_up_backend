"""PulseUp API: fábrica de la aplicación Flask."""
import sqlite3

from flask import Flask

from config import cargar_config
from pulseup.core.errors import registrar_manejadores
from pulseup.core.esquema import crear_esquema, sembrar_roles
from pulseup.core.semillas import sembrar_catalogo


def inicializar_base_de_datos(db_name):
    """Crea las tablas que falten y siembra los datos base. Es seguro repetirlo."""
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    try:
        crear_esquema(conn)
        sembrar_roles(conn)
        sembrar_catalogo(conn)
        conn.commit()
    finally:
        conn.close()


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.update(cargar_config(overrides))

    from pulseup.modules.auth.routes import auth_bp
    from pulseup.modules.ejercicios.routes import ejercicios_bp
    from pulseup.modules.perfil_fisico.routes import perfil_fisico_bp
    from pulseup.modules.plan.routes import plan_bp
    from pulseup.modules.recomendaciones.routes import recomendaciones_bp
    from pulseup.modules.rutinas.routes import rutinas_bp
    from pulseup.modules.usuarios.routes import usuarios_bp

    for blueprint in (auth_bp, usuarios_bp, ejercicios_bp, rutinas_bp, plan_bp, perfil_fisico_bp, recomendaciones_bp):
        app.register_blueprint(blueprint)

    registrar_manejadores(app)
    inicializar_base_de_datos(app.config["DB_NAME"])
    return app
