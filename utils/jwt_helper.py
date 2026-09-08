import jwt
import datetime
from config import SECRET_KEY

def generar_token(id_usuario, roles):
    payload = {
        "id_usuario": id_usuario,
        "roles": roles,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decodificar_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])