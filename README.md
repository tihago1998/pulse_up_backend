# PulseUp Backend

API REST de PulseUp, app móvil de hábitos saludables. Proyecto académico SENA,
Tecnología en Análisis y Desarrollo de Software (ADSO), Ficha 3223873.

> El cliente móvil Android está en el repositorio `pulseup_adroid_studio`.

## Problema y solución

La app necesita guardar y proteger los datos de cada persona, y controlar qué
puede hacer cada rol. Este backend ofrece una API REST con autenticación por
token y permisos por rol, validados siempre en el servidor.

## Características

- Registro e inicio de sesión con JWT.
- Roles: Administrador, Usuario y SuperAdministrador.
- Administración de usuarios: listar, cambiar rol, eliminar y estadísticas.
- Hábitos por usuario.
- Perfil: editar datos y cambiar contraseña.

## Estado de los módulos

| Módulo                                    | Estado       |
| ----------------------------------------- | ------------ |
| Autenticación (registro, login, JWT)      | Implementado |
| Roles y administración de usuarios        | Implementado |
| Perfil (editar datos, cambiar contraseña) | Implementado |
| Hábitos                                   | Implementado |
| Catálogo de ejercicios y rutinas          | Implementado |
| Sesiones de entrenamiento y progreso      | Pendiente    |
| Alimentación                              | Pendiente    |
| Sueño                                     | Pendiente    |

### Endpoints de ejercicio (requieren token)

| Método | Ruta                          | Descripción                                          |
| ------ | ----------------------------- | ---------------------------------------------------- |
| GET    | `/api/ejercicios/`            | Catálogo. Filtros: `musculo`, `equipo`, `nivel`, `q` |
| GET    | `/api/ejercicios/filtros`     | Valores disponibles para los filtros                 |
| GET    | `/api/ejercicios/<id>`        | Detalle con instrucciones                            |
| GET    | `/api/rutinas/`               | Plantillas + rutinas propias. Filtros: `objetivo`, `nivel` |
| GET    | `/api/rutinas/<id>`           | Rutina con sus ejercicios en orden                   |
| POST   | `/api/rutinas/`               | Crear rutina propia                                  |
| DELETE | `/api/rutinas/<id>`           | Eliminar una rutina propia (las plantillas no)       |

El catálogo (48 ejercicios) y las 7 rutinas plantilla se cargan solos al
arrancar, sin duplicarse (`pulseup/seeds/`).

## Tecnologías

Python, Flask y SQLite, con arquitectura por capas (routes → service → repository). Las dependencias y sus versiones
están en `requirements.txt`.

## Requisitos previos

- Python 3 y pip
- Git

## Instalación

```bash
git clone https://github.com/tihago1998/pulse_up_backend.git
cd pulse_up_backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

La aplicación lee sus ajustes de variables de entorno. Copia el archivo de ejemplo y define tu propia clave:

```bash
copy .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Pega la clave generada en `PULSEUP_SECRET_KEY` dentro de `.env`. Ese archivo no se sube al repositorio. Si falta la clave, la aplicación no arranca y muestra un mensaje indicándolo.

| Variable             | Obligatoria | Descripción                                            |
| -------------------- | ----------- | ------------------------------------------------------ |
| `PULSEUP_SECRET_KEY` | Sí          | Clave para firmar los tokens JWT                       |
| `PULSEUP_DB_NAME`    | No          | Archivo de la base de datos (por defecto `pulseup.db`) |
| `PULSEUP_HOST`       | No          | Dirección de escucha (por defecto `0.0.0.0`)           |
| `PULSEUP_PORT`       | No          | Puerto (por defecto `5050`)                            |
| `PULSEUP_DEBUG`      | No          | Modo de depuración (por defecto `true`)                |

## Ejecución

```bash
python app.py
```

El servidor queda en el puerto 5050. La base de datos SQLite se crea sola en el
primer arranque, con los roles iniciales.

## Pruebas

```
pip install -r requirements-dev.txt
python -m pytest -q tests
```

## Estructura

```
app.py                 Punto de entrada (app = create_app())
config.py              Configuración desde variables de entorno
pulseup/
  __init__.py          Fábrica de la app y creación de tablas
  core/                Piezas compartidas: BD, seguridad, auth, errores, roles
  modules/
    auth/              Registro e inicio de sesión
    usuarios/          Usuarios, perfil y roles
    habitos/           Hábitos y resumen del calendario
    ejercicios/        Catálogo de ejercicios con filtros
    rutinas/           Plantillas y rutinas propias
    <módulo>/          routes.py (HTTP) → service.py (reglas) → repository.py (SQL)
tests/                 Pruebas del contrato de la API
```

## Autores

- Santiago Varela Peña: desarrollador full stack, líder del proyecto
- Sebastián Navarro López: desarrollador full stack

Aprendices ADSO SENA, Ficha 3223873. Las responsabilidades son compartidas
entre backend y aplicación Android.

## Licencia

MIT. Ver `LICENSE`.
