"""Errores de la aplicación. Los servicios los lanzan y Flask los convierte en JSON."""
from flask import jsonify


class ErrorApp(Exception):
    status = 400

    def __init__(self, mensaje, status=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        if status is not None:
            self.status = status


class SolicitudInvalida(ErrorApp):
    status = 400


class NoAutenticado(ErrorApp):
    status = 401


class Prohibido(ErrorApp):
    status = 403


class NoEncontrado(ErrorApp):
    status = 404


class Conflicto(ErrorApp):
    status = 409


def registrar_manejadores(app):
    @app.errorhandler(ErrorApp)
    def _error_app(error):
        return jsonify({"error": error.mensaje}), error.status

    @app.errorhandler(404)
    def _no_encontrado(_):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def _metodo_no_permitido(_):
        return jsonify({"error": "Método no permitido"}), 405

    @app.errorhandler(500)
    def _error_interno(_):
        return jsonify({"error": "Error interno del servidor"}), 500
