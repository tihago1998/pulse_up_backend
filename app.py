"""Punto de entrada. `python app.py` para desarrollo; `gunicorn app:app` para producción."""
from pulseup import create_app

app = create_app()

if __name__ == "__main__":
    # host 0.0.0.0 permite que el emulador Android (10.0.2.2) se conecte
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
