"""Forma JSON de un usuario. Aquí se garantiza que `password_hash` NUNCA se filtre."""


def usuario_a_json(usuario, roles):
    return {
        "id_usuario": usuario["id_usuario"],
        "nombre": usuario["nombre"],
        "email": usuario["email"],
        "roles": roles,
    }
