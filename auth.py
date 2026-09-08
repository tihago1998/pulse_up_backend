import jwt  # librería para crear y verificar tokens JWT (la "credencial" de sesión)
import datetime  # para calcular cuándo expira el token
from werkzeug.security import generate_password_hash, check_password_hash
# generate_password_hash: convierte una contraseña en texto plano en un hash seguro
# check_password_hash: compara una contraseña en texto plano contra un hash guardado
from database import get_connection  # reutilizamos la conexión que ya definimos

# Clave secreta usada para firmar los tokens. Solo el servidor la conoce.
# En un proyecto real esto NUNCA se deja escrito así en el código (se usa una variable de entorno),
# pero para el proyecto de formación está bien mantenerlo simple.
SECRET_KEY = "pulseup-clave-secreta-2026"

def registrar_usuario(nombre, email, password):
    conn = get_connection()
    cur = conn.cursor()

    # Verificamos que el correo no esté ya registrado
    cur.execute("SELECT id_usuario FROM usuario WHERE email = ?", (email,))
    if cur.fetchone():
        conn.close()
        return None, "El correo ya está registrado"

    # Nunca guardamos la contraseña tal cual: la convertimos en un hash irreversible
    password_hash = generate_password_hash(password)

    cur.execute(
        "INSERT INTO usuario (nombre, email, password_hash) VALUES (?, ?, ?)",
        (nombre, email, password_hash)
    )
    id_usuario = cur.lastrowid  # obtiene el id que SQLite le acaba de asignar al nuevo usuario

    # Todo usuario nuevo nace con rol "Usuario" (id_rol = 2), nunca Administrador
    cur.execute(
        "INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (?, 2)",
        (id_usuario,)
    )

    conn.commit()
    conn.close()
    return id_usuario, None  # None significa "no hubo error"

def login_usuario(email, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM usuario WHERE email = ?", (email,))
    usuario = cur.fetchone()

    # Si no existe el usuario, O la contraseña no coincide con el hash guardado,
    # devolvemos el mismo mensaje genérico (por seguridad: no revelamos cuál de las dos falló)
    if not usuario or not check_password_hash(usuario["password_hash"], password):
        conn.close()
        return None, "Correo o contraseña incorrectos"

    # Buscamos todos los roles que tiene este usuario (normalmente solo uno)
    cur.execute("""
        SELECT r.nombre_rol FROM rol r
        JOIN usuario_rol ur ON r.id_rol = ur.id_rol
        WHERE ur.id_usuario = ?
    """, (usuario["id_usuario"],))
    roles = [row["nombre_rol"] for row in cur.fetchall()]
    conn.close()

    # Generamos el token que la app va a guardar y enviar en cada petición futura
    token = generar_token(usuario["id_usuario"], roles)

    return {
        "token": token,
        "usuario": {
            "id_usuario": usuario["id_usuario"],
            "nombre": usuario["nombre"],
            "email": usuario["email"],
            "roles": roles
        }
    }, None

def generar_token(id_usuario, roles):
    # El "payload" es la información que viaja dentro del token (visible si se decodifica,
    # pero no se puede modificar sin invalidar la firma)
    payload = {
        "id_usuario": id_usuario,
        "roles": roles,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # expira en 24 horas
    }
    # jwt.encode firma el payload con la clave secreta, generando el token final
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")