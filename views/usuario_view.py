# Convierte los datos internos de un usuario al formato JSON que se envía al cliente.
# Aquí es donde garantizamos que password_hash NUNCA se filtre.

def usuario_a_json(usuario_dict, roles):
    return {
        "id_usuario": usuario_dict["id_usuario"],
        "nombre": usuario_dict["nombre"],
        "email": usuario_dict["email"],
        "roles": roles
    }

def lista_usuarios_a_json(usuarios_con_roles):
    return {"usuarios": usuarios_con_roles}