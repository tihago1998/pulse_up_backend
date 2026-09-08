from flask import Flask
from models.database import crear_tablas
from controllers.auth_controller import auth_bp
from controllers.users_controller import users_bp

# Creamos la aplicación Flask
app = Flask(__name__)

# Registramos los Blueprints: le decimos a Flask "estas rutas también existen"
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)

if __name__ == "__main__":
    # Antes de arrancar el servidor, nos aseguramos de que las tablas existan
    crear_tablas()

    # host="0.0.0.0" permite que el emulador Android (vía 10.0.2.2) pueda conectarse
    # debug=True reinicia el servidor automáticamente cada vez que guardas un cambio
    app.run(host="0.0.0.0", port=5050, debug=True)