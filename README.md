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
| Ejercicio                                 | Pendiente    |
| Alimentación                              | Pendiente    |
| Sueño                                     | Pendiente    |

Las tablas de ejercicio, alimentación y sueño ya existen en el esquema de la
base de datos; faltan sus endpoints.

## Tecnologías

Python, Flask y SQLite, con arquitectura MVC. Las dependencias y sus versiones
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

## Ejecución

```bash
python app.py
```

El servidor queda en el puerto 5050. La base de datos SQLite se crea sola en el
primer arranque, con los roles iniciales.

## Pruebas

Pendiente.

## Estructura

```
app.py            Punto de entrada y registro de rutas
config.py         Configuración
controllers/      Lógica de cada endpoint
models/           Acceso a datos (SQLite)
views/            Formato de las respuestas
middleware/       Validación de token y roles
utils/            Utilidades (JWT)
```

## Autores

- Santiago Varela Peña: desarrollador full stack, líder del proyecto
- Sebastián Navarro López: desarrollador full stack

Aprendices ADSO SENA, Ficha 3223873. Las responsabilidades son compartidas
entre backend y aplicación Android.

## Licencia

MIT. Ver `LICENSE`.
